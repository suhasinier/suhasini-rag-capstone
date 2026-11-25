
"""Week 10 document lifecycle: tombstone and re-ingest."""

from __future__ import annotations

import time
import uuid

from qdrant_client.models import (
    FieldCondition,
    Filter,
    IsEmptyCondition,
    MatchValue,
    PayloadField,
    PointStruct,
)

from src.rag import cache
from src.ingest.pipeline import (
    parse_document,
    create_chunks,
    scrub_document_chunks,
    enrich_metadata,
    create_embeddings,
)

KB_VERSION = "2"


def tombstone_source(store, source: str) -> int:
    """Mark all currently live chunks belonging to a source as deleted."""

    live_source_filter = Filter(
        must=[
            FieldCondition(
                key="source",
                match=MatchValue(value=source),
            ),
            IsEmptyCondition(
                is_empty=PayloadField(key="deleted_at")
            ),
        ]
    )

    pre_count = store.client.count(
        collection_name=store.collection,
        count_filter=live_source_filter,
        exact=True,
    ).count

    store.client.set_payload(
        collection_name=store.collection,
        payload={"deleted_at": time.time()},
        points=live_source_filter,
        wait=True,
    )

    return pre_count


def ingest_or_update_source(
    store,
    source: str,
    body: str,
    doc_type: str = "pdf",
    clear_cache_after: bool = True,
) -> dict:
    """Tombstone old chunks, insert updated chunks, and clear cache."""

    # 1. Tombstone the old version.
    n_tombstoned = tombstone_source(store, source)

    # 2. Split the supplied document text into chunks.
    from wk08_pipeline import chunk_recursive

    raw_chunks = [
        {
            "text": text,
            "page": None,
            "section_path": source,
        }
        for text in chunk_recursive(body, max_size=400)
        if text.strip()
    ]

    # 3. Apply the Week 8 PII scrubber.
    cleaned_chunks, _ = scrub_document_chunks(raw_chunks)

    # 4. Build metadata using the Week 8 metadata structure.
    from pathlib import Path
    from datetime import datetime, timezone

    source_path = Path(source)
    ingested_at = datetime.now(timezone.utc).isoformat()

    metadata_chunks = []

    for index, chunk in enumerate(cleaned_chunks):
        metadata = enrich_metadata(
            chunk,
            source_path,
            index,
            ingested_at,
        )

        metadata["kb_version"] = KB_VERSION
        metadata_chunks.append(metadata)

    # 5. Generate embeddings.
    vectors = create_embeddings(
        [chunk["text"] for chunk in metadata_chunks]
    )

    # 6. Insert new points with fresh UUIDs.
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=chunk,
        )
        for chunk, vector in zip(metadata_chunks, vectors)
    ]

    if points:
        store.client.upsert(
            collection_name=store.collection,
            points=points,
            wait=True,
        )

    # 7. Clear the semantic cache.
    cache_cleared = (
        cache.clear() if clear_cache_after else 0
    )

    return {
        "tombstoned": n_tombstoned,
        "ingested": len(points),
        "cache_cleared": cache_cleared,
    }
