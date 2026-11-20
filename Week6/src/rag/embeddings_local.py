"""Local embeddings via sentence-transformers — 384-dim vectors, free."""

from sentence_transformers import SentenceTransformer

_model = None


def _get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def embed(text: str) -> list[float]:
    """Embed one string. Returns 384 floats."""
    return _get_model().encode(
        text,
        normalize_embeddings=True
    ).tolist()