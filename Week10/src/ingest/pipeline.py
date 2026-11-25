
"""End-to-end ingestion pipeline for the Week 8 capstone corpus."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pymupdf
from dotenv import load_dotenv
from openai import OpenAI

from src.ingest.chunkers import TextChunk
from src.ingest.pii import scrub_chunks
from src.rag.qdrant_store import (
    QdrantStore,
    _get_client,
    ensure_collection,
    upsert_chunks_v2,
)

from wk08_pipeline import chunk_recursive, parse_docx, parse_html

load_dotenv()

EMBED_MODEL = "text-embedding-3-small"
MAX_CHUNK_SIZE = 400
BATCH_SIZE = 100

_openai_client = None


def get_openai_client():
    global _openai_client

    if _openai_client is None:
        _openai_client = OpenAI()

    return _openai_client


# STEP 1: READ DOCUMENTS

def parse_document(path: Path) -> list[dict]:
    """Read a document and preserve page or section information."""

    ext = path.suffix.lower()
    segments = []

    if ext == ".pdf":
        doc = pymupdf.open(str(path))

        for page_number, page in enumerate(doc, start=1):
            text = page.get_text().strip()

            if text:
                segments.append({
                    "text": text,
                    "page": page_number,
                    "section_path": path.stem,
                })

        doc.close()

    elif ext in (".html", ".htm"):
        text = parse_html(path)

        segments.append({
            "text": text,
            "page": None,
            "section_path": path.stem,
        })

    elif ext == ".docx":
        paragraphs = parse_docx(path)
        current_heading = path.stem

        for paragraph in paragraphs:
            style = paragraph["style"]

            if style.startswith("Heading"):
                current_heading = paragraph["text"]

            segments.append({
                "text": paragraph["text"],
                "page": None,
                "section_path": current_heading,
            })

    elif ext in (".md", ".txt"):
        text = path.read_text(encoding="utf-8")

        segments.append({
            "text": text,
            "page": None,
            "section_path": path.stem,
        })

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return segments


# STEP 2: CREATE CHUNKS

def create_chunks(path: Path, segments: list[dict]) -> list[dict]:
    """Split document segments into recursive chunks."""

    chunks = []

    for segment in segments:
        text_chunks = chunk_recursive(
            segment["text"],
            max_size=MAX_CHUNK_SIZE,
        )

        for text in text_chunks:
            if not text.strip():
                continue

            chunks.append({
                "text": text,
                "page": segment["page"],
                "section_path": segment["section_path"],
            })

    return chunks


# STEP 3: SCRUB PERSONAL INFORMATION

def scrub_document_chunks(chunks: list[dict]) -> tuple[list[dict], list[dict]]:
    """Reuse the existing Week 8 PII scrubber."""

    text_chunks = [
        TextChunk(
            text=chunk["text"],
            section_path=chunk["section_path"],
        )
        for chunk in chunks
    ]

    scrubbed, reports = scrub_chunks(
        text_chunks,
        use_presidio=True,
    )

    cleaned_chunks = []

    for original, cleaned, report in zip(chunks, scrubbed, reports):
        cleaned_chunks.append({
            **original,
            "text": cleaned.text,
            "pii_flags_count": report["n_redactions"],
        })

    return cleaned_chunks, reports


# STEP 4: ADD METADATA

def enrich_metadata(
    chunk: dict,
    path: Path,
    chunk_index: int,
    ingested_at: str,
) -> dict:
    """Add the nine metadata fields to each chunk."""

    return {
        "chunk_id": f"{path.stem}#{chunk_index}",
        "source": path.name,
        "doc_type": path.suffix.lstrip(".").lower(),
        "section_path": chunk["section_path"],
        "page": chunk["page"],
        "date": None,
        "language": "en",
        "version": None,
        "ingested_at": ingested_at,
        "text": chunk["text"],
        "pii_flags_count": chunk["pii_flags_count"],
    }


# STEP 5: CREATE EMBEDDINGS

def create_embeddings(texts: list[str]) -> list[list[float]]:
    """Create embeddings in batches of 100 chunks."""

    client = get_openai_client()
    vectors = []

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]

        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=batch,
        )

        ordered_data = sorted(
            response.data,
            key=lambda item: item.index,
        )

        vectors.extend(item.embedding for item in ordered_data)

        print(
            f"  Embedded {min(start + len(batch), len(texts))}"
            f"/{len(texts)} chunks"
        )

    return vectors


# STEP 6: INGEST THE COMPLETE CORPUS

def ingest_corpus(
    corpus_dir: Path = Path("data/corpus"),
    collection_name: str = "capstone_chunks_v2",
) -> dict:
    """Process the corpus and store enriched chunks in Qdrant."""

    corpus_dir = Path(corpus_dir)

    if not corpus_dir.exists():
        raise FileNotFoundError(
            f"Corpus directory not found: {corpus_dir}"
        )

    store = QdrantStore(
        client=_get_client(),
        collection=collection_name,
    )

    ensure_collection(store)

    all_chunks = []
    per_file = {}
    total_pii_flags = 0

    ingested_at = datetime.now(timezone.utc).isoformat()

    supported_types = {
        ".pdf", ".html", ".htm", ".docx", ".md", ".txt"
    }

    for path in sorted(corpus_dir.iterdir()):

        if not path.is_file() or path.suffix.lower() not in supported_types:
            continue

        try:
            segments = parse_document(path)

            extracted_chars = sum(
                len(segment["text"]) for segment in segments
            )

            if extracted_chars < 50:
                print(
                    f"  SKIPPED {path.name}: "
                    f"only {extracted_chars} characters extracted"
                )
                continue

            chunks = create_chunks(path, segments)

            cleaned_chunks, reports = scrub_document_chunks(chunks)

            file_chunks = []

            for index, chunk in enumerate(cleaned_chunks):
                metadata = enrich_metadata(
                    chunk,
                    path,
                    index,
                    ingested_at,
                )

                file_chunks.append(metadata)

            pii_count = sum(
                chunk["pii_flags_count"] for chunk in file_chunks
            )

            total_pii_flags += pii_count
            all_chunks.extend(file_chunks)

            per_file[path.name] = {
                "chunks": len(file_chunks),
                "pii_flags": pii_count,
            }

            print(
                f"  OK {path.name}: "
                f"{len(file_chunks)} chunks, "
                f"{pii_count} PII redactions"
            )

        except Exception as error:
            print(f"  FAILED {path.name}: {error}")

    if not all_chunks:
        raise ValueError("No chunks were created. Nothing to embed.")

    print(f"\nCreating embeddings for {len(all_chunks)} chunks...")

    texts = [chunk["text"] for chunk in all_chunks]
    vectors = create_embeddings(texts)

    print(f"\nStoring chunks in {collection_name}...")

    upsert_chunks_v2(
        store,
        all_chunks,
        vectors,
    )

    return {
        "n_files": len(per_file),
        "n_chunks": len(all_chunks),
        "n_pii_flags": total_pii_flags,
        "per_file": per_file,
    }


if __name__ == "__main__":

    stats = ingest_corpus()

    print("\n========== WEEK 8 INGESTION SUMMARY ==========")
    print(f"Files ingested : {stats['n_files']}")
    print(f"Total chunks   : {stats['n_chunks']}")
    print(f"PII redactions : {stats['n_pii_flags']}")
    print("==============================================")
