
"""Update a single document in the capstone knowledge base."""

import sys
from pathlib import Path

import pymupdf

from src.rag.pipeline import ingest_or_update_source
from src.rag.qdrant_store import load_store


def main(doc_path: str):
    path = Path(doc_path)

    assert path.exists(), f"Not found: {path}"

    # Extract text from the PDF, one page at a time.
    with pymupdf.open(path) as pdf:
        body = "\n\n".join(page.get_text() for page in pdf)

    source = path.name

    store = load_store()
    result = ingest_or_update_source(store, source, body)

    print(f"Update complete for {source}:")
    print(f"  Tombstoned: {result['tombstoned']} old chunks")
    print(f"  Ingested:   {result['ingested']} new chunks")
    print(f"  Cache cleared: {result['cache_cleared']} entries")


if __name__ == "__main__":
    main(sys.argv[1])
