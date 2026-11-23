
"""Step-back query rewriting for the Week 9 capstone Stretch activity."""

from openai import OpenAI
from src.rag.retrieval import dense_search, rrf_fuse

_openai = None


def _get_openai():
    global _openai
    if _openai is None:
        _openai = OpenAI()
    return _openai


def step_back_retrieve(query: str, k: int = 3) -> list[dict]:
    """Generate a broader question, retrieve for both questions, and combine."""

    openai = _get_openai()

    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[{
            "role": "user",
            "content": (
                "Given a specific question, write a more general version that "
                "would return the background needed to answer the specific question. "
                "Return only the general question.\n\n"
                f"Specific: {query}\nGeneral:"
            )
        }],
    )

    general = resp.choices[0].message.content.strip()

    ranked_lists = [
        dense_search(query, k=5),
        dense_search(general, k=5)
    ]

    return rrf_fuse(ranked_lists, k=60, top_n=k)
