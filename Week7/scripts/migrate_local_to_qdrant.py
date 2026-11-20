
"""Generate local MiniLM embeddings and store them in Qdrant."""

import json
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from the repository root.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from src.rag.embeddings_local import embed_local
from src.rag.qdrant_store import (
    QdrantStore,
    load_store,
    ensure_collection,
    upsert_chunks,
    collection_size,
)

# Week7 project directory
WEEK7_DIR = Path(__file__).resolve().parents[1]

# Existing Week6 file containing the original text chunks
INDEX_PATH = WEEK7_DIR.parent / "Week6" / "data" / "embeddings_large.json"

LOCAL_COLLECTION = "capstone_chunks_local"
LOCAL_DIMENSION = 384
BATCH_SIZE = 32


def main():
    print(f"Loading chunks from: {INDEX_PATH}")

    with INDEX_PATH.open(encoding="utf-8") as f:
        index = json.load(f)

    # Extract only the original text and metadata.
    # We deliberately ignore the existing OpenAI vectors.
    chunks = [
        {
            key: item[key]
            for key in ("chunk_id", "source_id", "text")
        }
        for item in index
    ]

    print(f"Chunks loaded: {len(chunks)}")

    # Generate local embeddings in batches.
    texts = [chunk["text"] for chunk in chunks]
    vectors = []

    print("Generating local MiniLM embeddings...")

    for start in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[start:start + BATCH_SIZE]
        batch_vectors = embed_local(batch_texts)
        vectors.extend(batch_vectors)

        print(f"Embedded {len(vectors)}/{len(texts)} chunks")

    # Verify the embedding output.
    if len(vectors) != len(chunks):
        raise RuntimeError("Chunk and vector counts do not match.")

    if any(len(vector) != LOCAL_DIMENSION for vector in vectors):
        raise RuntimeError("Expected 384-dimensional vectors.")

    # Reuse the existing Qdrant connection, but point to a new collection.
    existing_store = load_store()

    local_store = QdrantStore(
        client=existing_store.client,
        collection=LOCAL_COLLECTION,
    )

    ensure_collection(local_store, dimension=LOCAL_DIMENSION)

    print(f"Storing vectors in '{LOCAL_COLLECTION}'...")
    upsert_chunks(local_store, chunks, vectors)

    # Confirm the number of stored points.
    total = collection_size(local_store)

    print("\nLocal migration completed.")
    print(f"Collection: {LOCAL_COLLECTION}")
    print(f"Chunks processed: {len(chunks)}")
    print(f"Vector dimensions: {LOCAL_DIMENSION}")
    print(f"Points in Qdrant: {total}")


if __name__ == "__main__":
    main()
