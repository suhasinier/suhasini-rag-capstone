
"""Local Qdrant retrieval using MiniLM embeddings."""

from src.rag.embeddings_local import embed_local
from src.rag.qdrant_store import QdrantStore


def retrieve_local(store: QdrantStore, query: str, k: int = 3):
    """Retrieve the top-k chunks using local MiniLM embeddings."""

    # Convert the user's question into a 384-dimensional vector.
    query_vector = embed_local([query])[0]

    # Search the selected Qdrant collection.
    results = store.client.query_points(
        collection_name=store.collection,
        query=query_vector,
        limit=k,
    ).points

    # Return the retrieved text and its source information.
    return [
        {
            "chunk_id": hit.payload["chunk_id"],
            "source_id": hit.payload["source_id"],
            "text": hit.payload["text"],
            "score": hit.score,
        }
        for hit in results
    ]
