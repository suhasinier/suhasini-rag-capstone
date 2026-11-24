"""MP2 · Mini-RAG — Starter Template
====================================

You'll build a complete RAG pipeline over the Sherlock Holmes corpus in this
file. Fill in every TODO. The reference solution is ~250 lines, but yours can
be shorter or longer — what matters is that it works end-to-end.

Pipeline you're building:
    corpus/*.txt  →  chunks  →  embeddings  →  Qdrant
                                                  ↓
                              question  →  retrieve  →  answer + citations

Run sequence (once you've filled in the TODOs):
    pip install -r requirements.txt
    source .env                 # exports your OpenAI + Qdrant credentials
    python mp2_rag.py ingest    # builds the collection (run once)
    python mp2_rag.py ask       # interactive Q&A loop
    python mp2_rag.py validate  # runs against data/predefined_questions.jsonl

Tip: get the CORE pipeline working FIRST (Steps 1-7 below), THEN come back to
polish and add your 3 questions. Don't try to perfect each step before moving
on — you'll learn more from a rough end-to-end loop than a polished half.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from dotenv import load_dotenv

load_dotenv()

# ─── Configuration ──────────────────────────────────────────────────────

CORPUS_DIR        = Path(__file__).parent / "corpus"
DATA_DIR          = Path(__file__).parent / "data"
COLLECTION_NAME   = "mp2_sherlock"
EMBEDDING_MODEL   = "text-embedding-3-small"
EMBEDDING_DIM     = 1536
CHAT_MODEL        = "gpt-4o-mini"
TARGET_CHUNK_SIZE = 500   # characters
CHUNK_OVERLAP     = 80    # characters

openai = OpenAI()
qdrant = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ.get("QDRANT_API_KEY"),
)


# ─── Step 1: Load the corpus ────────────────────────────────────────────

def load_corpus(corpus_dir: Path) -> list[dict[str, Any]]:
    """Read every .txt file in the corpus directory.

    Returns a list of dicts, each with: source (filename), title (first line),
    and text (full content).

    TODO:
      - Iterate over every *.txt file in corpus_dir (use Path.glob)
      - For each file, read its text and extract the first non-empty line as title
      - Return the list of doc dicts
    """
    docs = []

    for file_path in corpus_dir.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        lines = text.splitlines()
        title = next(line.strip() for line in lines if line.strip())

        docs.append({
            "source": file_path.name,
            "title": title,
            "text": text
        })

    return docs


# ─── Step 2: Chunk each document ────────────────────────────────────────

def chunk_document(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Split a document into smaller chunks.

    Each chunk should be a dict with: source, title, section, text.

    Approach (your choice):
      - Simple: fixed-size windows (split text into N-character chunks with overlap)
      - Smarter: split on paragraph boundaries (\\n\\n), then pack paragraphs
        into chunks up to TARGET_CHUNK_SIZE characters

    The reference solution uses the smarter approach, plus heuristic
    section-header detection (short lines without terminal punctuation).
    Either approach is acceptable.

    TODO:
      - Pick an approach
      - Implement it
      - Return list of chunk dicts
    """
    chunks = []

    text = doc["text"]

    step_size = TARGET_CHUNK_SIZE - CHUNK_OVERLAP

    for start in range(0, len(text), step_size):

        end = start + TARGET_CHUNK_SIZE

        chunk_text = text[start:end].strip()

        if not chunk_text:
            continue

        chunk_number = len(chunks) + 1

        chunks.append({
            "source": doc["source"],
            "title": doc["title"],
            "section": f"Chunk {chunk_number}",
            "text": chunk_text
        })

    return chunks


# ─── Step 3: Embed text ─────────────────────────────────────────────────

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch-embed a list of texts using OpenAI's embedding model.

    Returns a list of 1536-dim float vectors (same order as inputs).

    TODO:
      - Call openai.embeddings.create with EMBEDDING_MODEL and the texts
      - Extract the embedding vectors from the response
    """
    """Batch-embed a list of texts using OpenAI's embedding model.

    Returns a list of 1536-dim float vectors (same order as inputs).
    """

    response = openai.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )

    embeddings = [item.embedding for item in response.data]

    return embeddings


# ─── Step 4: Set up the Qdrant collection ───────────────────────────────

def setup_collection() -> None:
    """Create (or recreate) the Qdrant collection.

    TODO:
      - Use qdrant.recreate_collection
      - VectorParams with EMBEDDING_DIM and Distance.COSINE
    """
    """Create (or recreate) the Qdrant collection."""

    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_DIM,
            distance=Distance.COSINE
        )
    )

    print(f"Collection '{COLLECTION_NAME}' created.")


# ─── Step 5: Ingest chunks into Qdrant ──────────────────────────────────

def ingest_chunks(chunks: list[dict[str, Any]]) -> None:
    """Embed every chunk and upsert into Qdrant.

    TODO:
      - Call embed_texts on the chunk texts
      - Build PointStruct objects (id=uuid, vector, payload=chunk dict)
      - qdrant.upsert
    """
    """Embed every chunk and upsert into Qdrant."""

    texts = [chunk["text"] for chunk in chunks]

    vectors = embed_texts(texts)

    points = []

    for chunk, vector in zip(chunks, vectors):
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=chunk
        )

        points.append(point)

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print(f"Ingested {len(points)} chunks into Qdrant.")


# ─── Step 6: Retrieve ───────────────────────────────────────────────────

def retrieve(query: str, k: int = 3) -> list[dict[str, Any]]:
    """Retrieve top-k chunks for a query.

    TODO:
      - Embed the query
      - qdrant.search with the query vector, limit=k
      - Return list of chunk dicts (include score for citations)
    """
    query_vector = embed_texts([query])[0]

    response = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=k,
        with_payload=True
    )

    results = response.points

    retrieved_chunks = []

    for result in results:
        chunk = result.payload.copy()
        chunk["score"] = result.score
        retrieved_chunks.append(chunk)

    return retrieved_chunks


# ─── Step 7: Generate the answer ────────────────────────────────────────

SYSTEM_PROMPT = """You are a helpful assistant answering questions about a small
collection of Sherlock Holmes stories. You will be given the user's question and
several relevant excerpts. Use ONLY the provided excerpts to answer. If the
excerpts don't contain the answer, say so plainly. Cite the source (story title
+ section) in your answer."""


def answer(question: str, k: int = 3) -> dict[str, Any]:
    """End-to-end: retrieve, format context, call LLM, return result.

    TODO:
      - Call retrieve(question, k=k)
      - Format the retrieved chunks into a context string
        (include "[Source: <title> — <section>]" before each)
      - Call openai.chat.completions.create with SYSTEM_PROMPT and the user message
      - Return dict with: question, answer, citations, latency_ms
    """
    start_time = time.perf_counter()

    # Step 1: Retrieve relevant chunks
    chunks = retrieve(question, k=k)

    # Step 2: Format the retrieved chunks into context
    context_parts = []

    for chunk in chunks:
        source_label = (
            f"[Source: {chunk['title']} — {chunk['section']}]"
        )

        context_parts.append(
            f"{source_label}\n{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    # Step 3: Send the question and context to the LLM
    response = openai.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Retrieved excerpts:\n{context}"
                )
            }
        ],
        temperature=0.0
    )

    # Step 4: Extract the generated answer
    answer_text = response.choices[0].message.content

    # Step 5: Prepare citation details
    citations = [
        {
            "source": chunk["source"],
            "title": chunk["title"],
            "section": chunk["section"],
            "score": chunk["score"]
        }
        for chunk in chunks
    ]

    # Step 6: Calculate total processing time
    latency_ms = round(
        (time.perf_counter() - start_time) * 1000
    )

    # Step 7: Return the result
    return {
        "question": question,
        "answer": answer_text,
        "citations": citations,
        "latency_ms": latency_ms
    }


# ─── Validation harness (provided — do not modify) ──────────────────────

def validate_against(jsonl_path: Path) -> None:
    questions = [json.loads(line) for line in jsonl_path.read_text().splitlines() if line.strip()]
    print(f"\n  Validating {len(questions)} questions from {jsonl_path.name}…\n")

    hits = 0
    for q in questions:
        result = answer(q["question"], k=3)
        cited_sources = {cit["source"] for cit in result["citations"]}
        source_hit = q["expected_source"] in cited_sources

        ans_lower = result["answer"].lower()
        facts_hit = sum(1 for fact in q.get("expected_facts", []) if fact.lower() in ans_lower)
        facts_total = len(q.get("expected_facts", []))

        verdict = "✓" if source_hit else "✗"
        print(f"  {verdict} {q['id']}")
        print(f"      Q: {q['question']}")
        print(f"      Cited: {', '.join(cited_sources)}")
        print(f"      Expected: {q['expected_source']}")
        print(f"      Facts matched: {facts_hit}/{facts_total}")
        print(f"      Latency: {result.get('latency_ms', '?')}ms")
        print()
        if source_hit:
            hits += 1

    print(f"  Source-match: {hits}/{len(questions)}")


# ─── CLI (provided — do not modify) ─────────────────────────────────────

def cmd_ingest() -> None:
    print("→ Loading corpus…")
    docs = load_corpus(CORPUS_DIR)
    print(f"  {len(docs)} documents loaded")

    print("→ Chunking…")
    all_chunks: list[dict[str, Any]] = []
    for doc in docs:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"  {doc['source']}: {len(chunks)} chunks")

    print(f"→ Total chunks: {len(all_chunks)}")
    print("→ Setting up Qdrant collection…")
    setup_collection()

    print("→ Ingesting…")
    ingest_chunks(all_chunks)
    print("\n✓ Done. Try: python mp2_rag.py ask")


def cmd_ask() -> None:
    print("Mini-RAG over the Sherlock Holmes corpus.")
    print("Type your question. Empty line or Ctrl-C to exit.\n")
    while True:
        try:
            q = input("? ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not q:
            return
        result = answer(q, k=3)
        print(f"\n{result['answer']}\n")
        print("  Sources:")
        for c in result["citations"]:
            print(f"    - {c['title']} — {c['section']}")
        print(f"  Latency: {result.get('latency_ms', '?')}ms\n")


def cmd_validate() -> None:
    validate_against(DATA_DIR / "predefined_questions.jsonl")
    learner_path = DATA_DIR / "learner_questions.jsonl"
    if learner_path.exists():
        first = json.loads(learner_path.read_text().splitlines()[0])
        if not first["question"].startswith("Replace this"):
            validate_against(learner_path)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "ingest":   cmd_ingest()
    elif cmd == "ask":    cmd_ask()
    elif cmd == "validate": cmd_validate()
    else:
        print(f"Unknown command: {cmd}\n")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

# ============================================================
# STEP 6 (OPTIONAL STRETCH): HYBRID SEARCH AND RERANKING
# ============================================================
# The following functions extend the original Mini-RAG pipeline.
# They are optional and are not required for the core project.
#
# This section adds:
# 1. BM25 keyword-based retrieval
# 2. Reciprocal Rank Fusion (RRF)
# 3. Cross-encoder reranking
# ============================================================

def simple_tokenize(text: str) -> list[str]:
    """Convert text into lowercase word tokens."""

    text = text.lower()

    return re.findall(r'[a-z0-9][a-z0-9\-/_]*', text)

def build_bm25_index(chunks: list[dict[str, Any]]):
    """Build a BM25 keyword-search index over the corpus chunks."""

    from rank_bm25 import BM25Okapi

    tokenized_chunks = [
        simple_tokenize(chunk["text"] + " " + chunk["title"])
        for chunk in chunks
    ]

    return BM25Okapi(tokenized_chunks)

_bm25_index = None
_bm25_chunks = None


def get_bm25_index():
    """Build the BM25 index once and reuse it."""

    global _bm25_index, _bm25_chunks

    if _bm25_index is None:
        docs = load_corpus(CORPUS_DIR)

        _bm25_chunks = [
            chunk
            for doc in docs
            for chunk in chunk_document(doc)
        ]

        _bm25_index = build_bm25_index(_bm25_chunks)

        print(f"BM25 index created with {len(_bm25_chunks)} chunks.")

    return _bm25_index, _bm25_chunks

def bm25_search(
    index,
    chunks: list[dict[str, Any]],
    query: str,
    k: int = 10
) -> list[dict[str, Any]]:
    """Search the BM25 index and return the top-k matching chunks."""

    tokens = simple_tokenize(query)

    scores = index.get_scores(tokens)

    ranked = sorted(
        zip(scores, chunks),
        key=lambda pair: pair[0],
        reverse=True
    )

    return [
        {
            "id": f"{chunk['source']}::{chunk['section']}",
            "doc": chunk,
            "score": float(score)
        }
        for score, chunk in ranked[:k]
    ]

def rrf_fuse(
    ranked_lists: list[list[dict[str, Any]]],
    k: int = 60,
    top_n: int = 10
) -> list[dict[str, Any]]:
    """Combine multiple ranked lists using Reciprocal Rank Fusion."""

    scores = {}
    docs = {}

    for ranked in ranked_lists:
        for rank, hit in enumerate(ranked, start=1):
            doc_id = hit["id"]

            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)

            if doc_id not in docs:
                docs[doc_id] = hit

    fused = sorted(
        scores.items(),
        key=lambda pair: pair[1],
        reverse=True
    )[:top_n]

    return [
        {**docs[doc_id], "rrf_score": score}
        for doc_id, score in fused
    ]
def dense_search_for_rrf(
    query: str,
    k: int = 10
) -> list[dict[str, Any]]:
    """Adapt dense retrieval results to the common RRF format."""

    dense_results = retrieve(query, k=k)

    return [
        {
            "id": f"{chunk['source']}::{chunk['section']}",
            "doc": chunk,
            "score": chunk["score"]
        }
        for chunk in dense_results
    ]

def hybrid_retrieve(
    query: str,
    k: int = 10
) -> list[dict[str, Any]]:
    """Retrieve and combine dense and BM25 search results."""

    # Step 1: Dense retrieval
    dense_results = dense_search_for_rrf(query, k=k)

    # Step 2: Get the BM25 index
    bm25_index, bm25_chunks = get_bm25_index()

    # Step 3: BM25 keyword retrieval
    bm25_results = bm25_search(
        bm25_index,
        bm25_chunks,
        query,
        k=k
    )

    # Step 4: Combine both ranked lists using RRF
    hybrid_results = rrf_fuse(
        [dense_results, bm25_results],
        top_n=k
    )

    return hybrid_results

# ─── Cross-encoder reranker ───────────────────────────────────────────

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker = None


def load_reranker():
    """Load the cross-encoder model once and reuse it."""

    global _reranker

    if _reranker is None:
        from sentence_transformers import CrossEncoder

        _reranker = CrossEncoder(RERANKER_MODEL)

    return _reranker

def rerank(
    query: str,
    candidates: list[dict[str, Any]],
    top_k: int = 3
) -> list[dict[str, Any]]:
    """Rerank candidate chunks using a cross-encoder."""

    reranker = load_reranker()

    pairs = [
        (query, hit["doc"]["text"])
        for hit in candidates
    ]

    scores = reranker.predict(pairs)

    scored = [
        {**hit, "rerank_score": float(score)}
        for hit, score in zip(candidates, scores)
    ]

    scored.sort(
        key=lambda hit: hit["rerank_score"],
        reverse=True
    )

    return scored[:top_k]

def answer_hybrid(question: str, k: int = 3) -> dict[str, Any]:
    """Generate an answer using hybrid retrieval and cross-encoder reranking."""

    start_time = time.perf_counter()

    # Step 1: Retrieve candidates using dense search + BM25 + RRF
    candidates = hybrid_retrieve(question, k=10)

    # Step 2: Rerank candidates using the cross-encoder
    results = rerank(question, candidates, top_k=k)

    # Step 3: Extract the original chunks
    chunks = [result["doc"] for result in results]

    # Step 4: Format retrieved chunks into context
    context_parts = []

    for chunk in chunks:
        source_label = (
            f"[Source: {chunk['title']} — {chunk['section']}]"
        )

        context_parts.append(
            f"{source_label}\n{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    # Step 5: Send question and context to the LLM
    response = openai.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Retrieved excerpts:\n{context}"
                )
            }
        ],
        temperature=0.0
    )

    # Step 6: Extract the generated answer
    answer_text = response.choices[0].message.content

    # Step 7: Prepare citation details
    citations = [
        {
            "source": result["doc"]["source"],
            "title": result["doc"]["title"],
            "section": result["doc"]["section"],
            "score": result["rerank_score"]
        }
        for result in results
    ]

    # Step 8: Calculate processing time
    latency_ms = round(
        (time.perf_counter() - start_time) * 1000
    )

    # Step 9: Return the result
    return {
        "question": question,
        "answer": answer_text,
        "citations": citations,
        "latency_ms": latency_ms
    }

