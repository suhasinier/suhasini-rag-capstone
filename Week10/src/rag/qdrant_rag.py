
"""Qdrant-backed RAG with semantic caching — W10."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from src.rag import cache
from src.rag.retrieval import retrieve


CHAT_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"

_openai_client = None


def _get_openai() -> OpenAI:
    """Create the OpenAI client only when it is first needed."""

    global _openai_client

    if _openai_client is None:
        _openai_client = OpenAI()

    return _openai_client


def _build_prompt(question: str, retrieved: list[dict]) -> str:
    """Build the prompt using the context returned by W9 retrieval."""

    system = (
        "You are a helpful assistant. Answer using ONLY the context. "
        "If the context does not contain the answer, say 'I don't know'."
    )

    context = "\n\n".join(
        f"[{i + 1}] {hit['doc'].get('text', '')}"
        for i, hit in enumerate(retrieved)
    )

    return (
        f"{system}\n\n"
        f"=== Context ===\n{context}\n\n"
        f"=== Question ===\n{question}\n\n"
        f"=== Answer ==="
    )


def ask_rag(
    question: str,
    k: int = 3,
    cache_threshold: float = 0.95,
) -> dict[str, Any]:
    """Check semantic cache first; run the full RAG pipeline on a miss."""

    client = _get_openai()

    # Layer 1: Create the query embedding and check semantic cache.
    q_vec = client.embeddings.create(
        model=EMBED_MODEL,
        input=[question],
    ).data[0].embedding

    hit = cache.lookup(
        q_vec,
        threshold=cache_threshold,
    )

    if hit:
        return {
            "answer": hit["answer"],
            "cache_hit": True,
            "similarity": hit["similarity"],
            "matched": hit["matched_question"],
        }

    # Cache miss: run the W9 hybrid retrieval + reranking pipeline.
    retrieved = retrieve(question, k=k)

    prompt = _build_prompt(question, retrieved)

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0.1,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    answer = response.choices[0].message.content

    # Store the answer and embedding for future queries.
    cache.put(
        question=question,
        embedding=q_vec,
        answer=answer,
    )

    return {
        "answer": answer,
        "cache_hit": False,
        "n_input_tokens": response.usage.prompt_tokens,
        "n_output_tokens": response.usage.completion_tokens,
        "n_cached_input_tokens": (
            getattr(response.usage, "prompt_tokens_details", None)
            and response.usage.prompt_tokens_details.cached_tokens
            or 0
        ),
        "retrieved": retrieved,
    }
