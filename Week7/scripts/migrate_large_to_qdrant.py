
"""Create large-model embeddings and store them in a separate Qdrant collection."""

import json
from pathlib import Path

from openai import OpenAI

from src.rag.qdrant_store import (
    load_large_store,
    ensure_collection,
    upsert_chunks,
    collection_size,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = REPO_ROOT / "Week6/data/embeddings_large.json"
EMBED_MODEL = "text-embedding-3-large"
BATCH_SIZE = 100


def main():
    print(f"Loading corpus chunks from {INDEX_PATH}...")

    with INDEX_PATH.open(encoding="utf-8") as f:
        index = json.load(f)

    chunks = [
        {key: item[key] for key in ("chunk_id", "source_id", "text")}
        for item in index
    ]

    print(f"Chunks loaded: {len(chunks)}")

    client = OpenAI()
    vectors = []

    print(f"Generating embeddings with {EMBED_MODEL}...")

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]

        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=[chunk["text"] for chunk in batch],
        )

        vectors.extend(
            item.embedding
            for item in sorted(response.data, key=lambda item: item.index)
        )

        print(f"Embedded {len(vectors)}/{len(chunks)} chunks")

    if len(vectors) != len(chunks):
        raise RuntimeError("The number of embeddings does not match the chunks.")

    if any(len(vector) != 3072 for vector in vectors):
        raise RuntimeError("Expected 3072-dimensional large-model embeddings.")

    store = load_large_store()
    ensure_collection(store, dimension=3072)

    print(f"Upserting into {store.collection}...")
    upsert_chunks(store, chunks, vectors)

    print(f"Migration complete. Points: {collection_size(store)}")


if __name__ == "__main__":
    main()
