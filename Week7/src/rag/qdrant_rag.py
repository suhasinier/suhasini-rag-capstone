
"""Qdrant-backed RAG for the capstone — W7 upgrade of W6's naive_rag.

Same public interface as W6's ask_rag: (question, store, k) → dict.
Storage layer swapped from JSON+numpy to Qdrant.
"""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from src.pipeline.settings import Settings
from src.rag.qdrant_store import QdrantStore, load_store


CHAT_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"

_client = None


def _openai() -> OpenAI:
    """Lazy-init the OpenAI client (unit tests can import without a key)."""

    global _client

    if _client is None:
        _client = OpenAI()

    return _client


def embed_query(text: str) -> list[float]:
    """Create an embedding for a single query."""

    resp = _openai().embeddings.create(
        model=EMBED_MODEL,
        input=[text],
    )

    return resp.data[0].embedding


def retrieve(
    store: QdrantStore,
    query: str,
    k: int = 3,
) -> list[dict[str, Any]]:
    """Embed the query and ask Qdrant for the top-k results."""

    q_vec = embed_query(query)

    results = store.client.query_points(
        collection_name=store.collection,
        query=q_vec,
        limit=k,
    ).points

    return [
        {
            "chunk_id": hit.payload["chunk_id"],
            "source_id": hit.payload["source_id"],
            "text": hit.payload["text"],
            "score": hit.score,
        }
        for hit in results
    ]

def retrieve_large(
    store: QdrantStore,
    query: str,
    k: int = 3,
) -> list[dict[str, Any]]:
    """Retrieve results using text-embedding-3-large."""

    response = _openai().embeddings.create(
        model="text-embedding-3-large",
        input=[query],
    )
    query_vector = response.data[0].embedding

    results = store.client.query_points(
        collection_name=store.collection,
        query=query_vector,
        limit=k,
    ).points

    return [
        {
            "chunk_id": hit.payload["chunk_id"],
            "source_id": hit.payload["source_id"],
            "text": hit.payload["text"],
            "score": hit.score,
        }
        for hit in results
    ]


SYSTEM = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "provided context. If the context does not contain the answer, say so "
    "plainly. Cite the source_id in square brackets after any fact you use."
)


def ask_rag(
    question: str,
    store: QdrantStore | None = None,
    settings: Settings | None = None,
    k: int = 3,
) -> dict[str, Any]:
    """Full pipeline: embed → retrieve → prompt → generate."""

    if store is None:
        store = load_store()

    retrieved = retrieve(store, question, k=k)

    context = "\n\n".join(
        f"[{hit['chunk_id']}] (source: {hit['source_id']})\n{hit['text']}"
        for hit in retrieved
    )

    resp = _openai().chat.completions.create(
        model=CHAT_MODEL,
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\n---\n\nQuestion: {question}",
            },
        ],
    )

    return {
        "answer": resp.choices[0].message.content,
        "sources": [hit["source_id"] for hit in retrieved],
        "chunk_ids": [hit["chunk_id"] for hit in retrieved],
        "tokens_in": resp.usage.prompt_tokens,
        "tokens_out": resp.usage.completion_tokens,
    }
