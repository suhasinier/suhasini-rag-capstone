
"""Qdrant vector store for the capstone.

Replaces W6's naive_rag.py in-memory list + JSON cache with a real
vector database. Same public interface — different engine underneath.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


COLLECTION_NAME = "capstone_chunks"
EMBEDDING_DIM = 1536  # text-embedding-3-small


@dataclass
class QdrantStore:
    """Wraps a Qdrant client and a collection name."""

    client: QdrantClient
    collection: str


def _get_client() -> QdrantClient:
    """Build a QdrantClient using QDRANT_URL and QDRANT_API_KEY."""

    url = os.environ.get("QDRANT_URL", "http://localhost:6333")
    api_key = os.environ.get("QDRANT_API_KEY") or None

    if api_key:
        return QdrantClient(url=url, api_key=api_key)

    return QdrantClient(url=url)


def load_store() -> QdrantStore:
    """Return a QdrantStore pointing at the capstone_chunks collection."""

    return QdrantStore(
        client=_get_client(),
        collection=COLLECTION_NAME,
    )


def load_large_store() -> QdrantStore:
    """Return a QdrantStore for the large-embedding comparison."""

    return QdrantStore(
        client=_get_client(),
        collection="capstone_chunks_large",
    )


def ensure_collection(store: QdrantStore, dimension: int = EMBEDDING_DIM) -> None:
    """Create the selected collection if it does not already exist."""

    existing = [
        collection.name
        for collection in store.client.get_collections().collections
    ]

    if store.collection in existing:
        return

    store.client.create_collection(
        collection_name=store.collection,
        vectors_config=VectorParams(
            size=dimension,
            distance=Distance.COSINE,
        ),
    )



def upsert_chunks(
    store: QdrantStore,
    chunks: list[dict],
    vectors: list[list[float]],
) -> None:
    """Store document chunks, their vectors, and metadata in Qdrant."""

    points = [
        PointStruct(
            id=idx,
            vector=vec,
            payload={
                "chunk_id": chunk["chunk_id"],
                "source_id": chunk["source_id"],
                "text": chunk["text"],
            },
        )
        for idx, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]

    store.client.upsert(
        collection_name=store.collection,
        points=points,
    )


def collection_size(store: QdrantStore) -> int:
    """Return the number of points in the collection."""

    info = store.client.get_collection(store.collection)
    return info.points_count or 0
