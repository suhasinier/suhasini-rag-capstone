# 1. Incident: Stale CBSE Answer After Document Update

**Summary:** The CBSE Knowledge Assistant continues returning an outdated answer from its semantic cache even after the corresponding source document has been updated.

## 2. Symptoms

- Users ask questions about a recently updated CBSE document but receive answers based on its older version.
- The assistant repeatedly returns the same outdated information even after the document update was completed.
- The document update operation reports successful tombstoning and ingestion of the updated document.
- The response metadata indicates a semantic cache hit for the affected question, if cache-hit information is exposed.
- Multiple users report the same outdated answer, indicating that the issue is not limited to one user's session.

## 3. Likely Root Cause

The likely root cause is a stale entry in the SQLite semantic cache (`results.db`, table `query_cache`). When the CBSE source document was updated, the old answer may not have been invalidated from the cache. The assistant uses a similarity threshold of 0.95, so a question similar to the previously cached question may retrieve the old answer without performing fresh retrieval from the updated document. Since the document update and tombstone checks reportedly completed successfully, cache invalidation is the primary issue to investigate rather than assuming that the old document chunks are still being retrieved.

## 4. Diagnostic Steps

Run all commands from the `Week10` project directory.

**1. Confirm the semantic cache hit.**

```bash
python3 - <<'PY'
from src.rag.qdrant_rag import ask_rag

question = "What is the CBSE scheme of studies for Class IX for 2026-27?"
result = ask_rag(question)

print("Cache hit:", result.get("cache_hit"))
print("Matched question:", result.get("matched"))
print("Similarity:", result.get("similarity"))
print("Answer:", result.get("answer"))
PY
```

Expected: `Cache hit: True`, similarity at or above `0.95`, and the outdated answer.

**2. Inspect live knowledge-base retrieval independently of the semantic cache.**

```bash
python3 - <<'PY'
from src.rag.retrieval import retrieve

question = "What is the CBSE scheme of studies for Class IX for 2026-27?"
results = retrieve(question, k=3)

for item in results:
    doc = item["doc"]
    print("Source:", doc.get("source"))
    print("Deleted at:", doc.get("deleted_at"))
    print("Text:", doc.get("text", "")[:500])
PY
```

Expected: Relevant chunks from the updated CBSE source document. `Deleted at: None` for every returned chunk. Confirm that the retrieved text reflects the updated document. A tombstoned chunk or missing updated content indicates a separate knowledge-base retrieval problem.

**3. Inspect the semantic-cache state and affected question.**

```bash
python3 - <<'PY'
import sqlite3
from src.rag import cache

print("Cache statistics:", cache.stats("./results.db"))

conn = sqlite3.connect("./results.db")
rows = conn.execute("""
    SELECT question, answer, hit_count, created_ts
    FROM query_cache
    WHERE question LIKE '%scheme of studies%'
    ORDER BY created_ts DESC
""").fetchall()

for row in rows:
    print(row)

conn.close()
PY
```

Expected: Cache statistics show the existing entries. The affected question has a stored answer and creation timestamp. Compare `created_ts` with the document-update time. An entry created before the update and containing the old answer confirms cache staleness.

## 5. Fix

**1. Clear the semantic cache.**

Run from the `Week10` project directory.

```bash
python3 - <<'PY'
from src.rag import cache

cleared = cache.clear("./results.db")
print("Cache entries cleared:", cleared)
PY
```

Expected: The number of deleted cache entries is displayed. This clears entries from the semantic cache table without deleting the knowledge base or its documents.

**2. Confirm that the cache is empty.**

```bash
python3 - <<'PY'
from src.rag import cache

print(cache.stats("./results.db"))
PY
```

Expected: `n_entries` is `0` and `total_hits` is `0`.

**3. Re-ask the original question to generate a fresh answer.**

```bash
python3 - <<'PY'
from src.rag.qdrant_rag import ask_rag

question = "What is the CBSE scheme of studies for Class IX for 2026-27?"
result = ask_rag(question)

print("Cache hit:", result.get("cache_hit"))
print("Answer:", result.get("answer"))
PY
```

Expected: `Cache hit: False` and an answer based on the updated CBSE document. The fresh answer is automatically stored in the semantic cache.

## 6. Verification

**1. Confirm that the first question generates a fresh answer.**

Expected: `cache_hit: False`. The answer must reflect the updated CBSE document, not its previous version.

**2. Ask the same question again.**

```bash id="g0r5va"
python3 - <<'PY'
from src.rag.qdrant_rag import ask_rag

question = "What is the CBSE scheme of studies for Class IX for 2026-27?"

result = ask_rag(question)

print("Cache hit:", result.get("cache_hit"))
print("Answer:", result.get("answer"))
PY
```

Expected: `cache_hit: True`. The returned answer must match the fresh answer generated in the previous step.

**3. Confirm that the cache contains the refreshed entry.**

```bash id="0y8l2f"
python3 - <<'PY'
from src.rag import cache

print("Cache statistics:", cache.stats("./results.db"))
PY
```

Expected: At least one cache entry exists, and the hit count reflects reuse of the refreshed answer.

## 7. Post-Incident Actions

1. **Enforce cache invalidation during document updates.** The current `update_document.py` calls `ingest_or_update_source()`, which clears the semantic cache by default. Add a regression test or CI check to ensure future changes do not disable cache clearing during document updates.

2. **Add a deployment safeguard.** Require document-update workflows to verify that the semantic cache has been cleared successfully before declaring an update complete.

3. **Communicate with affected users.** Notify the six users who received the outdated CBSE answer that the assistant has been refreshed. Ask them to recheck the answer and provide the corrected information where necessary.

4. **Improve cache monitoring.** Introduce cache-hit-rate monitoring and alert if the cache-hit rate remains above 90% for one hour. Investigate unusually high hit rates to identify possible cache-invalidation problems.

## 8. Time Budget

| Activity | Estimated time |
|---|---:|
| Diagnosis | 8 minutes |
| Fix and cache verification | 3 minutes |
| Post-incident actions and user communication | 15 minutes |
| **Total** | **Approximately 25 minutes** |

