
"""Build a CBSE index using local sentence-transformer embeddings."""

import argparse
import json
import sys
from pathlib import Path

# Locate the Week6 project folder
WEEK6_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WEEK6_ROOT))

# Import the local embedding function
from src.rag.embeddings_local import embed


# CBSE data file used by the existing build_index.py
INPUT_FILE = WEEK6_ROOT / "data" / "parsed_cbse.jsonl"


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split text into overlapping character-based chunks."""

    if len(text) <= size:
        return [text]

    chunks = []
    i = 0

    while i < len(text):
        end = min(i + size, len(text))
        chunks.append(text[i:end])

        if end == len(text):
            break

        i = end - overlap

    return chunks


def chunk_documents(
    documents: list[dict],
    size: int,
    overlap: int
) -> list[dict]:
    """Split every document into chunks with source information."""

    all_chunks = []

    for doc in documents:
        for chunk_idx, chunk in enumerate(
            chunk_text(doc["text"], size, overlap)
        ):
            all_chunks.append({
                "chunk_id": f"{doc['id']}#{chunk_idx}",
                "source_id": doc["id"],
                "text": chunk,
            })

    return all_chunks


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--overlap", type=int, required=True)
    parser.add_argument("--out", required=True)

    args = parser.parse_args()

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"CBSE parsed data not found: {INPUT_FILE}"
        )

    # Load the CBSE documents
    documents = []

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                record = json.loads(line)
                documents.append({
                    "id": record["source_id"],
                    "text": record["text"],
                })

    print(f"CBSE page documents loaded: {len(documents)}")

    # Split documents into chunks
    chunks = chunk_documents(
        documents,
        size=args.size,
        overlap=args.overlap
    )

    print(f"Chunks created: {len(chunks)}")

    # Generate a local embedding for every chunk
    for i, chunk in enumerate(chunks, start=1):
        chunk["vector"] = embed(chunk["text"])

        if i % 50 == 0 or i == len(chunks):
            print(f"Local embeddings generated: {i}/{len(chunks)}")

    # Save the local index
    output_path = Path(args.out)

    if not output_path.is_absolute():
        output_path = WEEK6_ROOT / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(chunks, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Local index saved: {output_path}")


if __name__ == "__main__":
    main()
