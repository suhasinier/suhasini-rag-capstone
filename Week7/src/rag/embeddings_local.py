
"""Local embeddings using Sentence Transformers.

Uses all-MiniLM-L6-v2 to generate normalised 384-dimensional vectors.
"""

# Lazy-load the model: it is loaded only when first needed.
_model = None


def _get_model():
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def embed_local(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings and return normalised 384-dim vectors."""

    vecs = _get_model().encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return vecs.tolist()
