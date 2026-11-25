# Week 10 Practice Assignment – Step-by-Step Completion Guide

## Purpose

This guide records the completion of the Week 10 Practice Assignment, **Write an Operations Runbook for a Likely Incident**, in the Vocareum capstone project.

**Project root:** `~/suhasini-rag-capstone/Week10`

**Runbook submission file:** `Week10/docs/runbooks/wk10_incident_stale_cache.md`

**Guide destination:** `Week10/guides/Week10_Assignment_Incident_Runbook_Guide.md`

The assignment requires eight sections, in this order:

1. Title and one-line summary
2. Symptoms (3–5 bullets)
3. Likely root cause (one paragraph)
4. Diagnostic steps (3–6 executable commands, ordered, with expected outputs)
5. Fix (ordered steps with exact commands)
6. Verification (2–3 concrete checks)
7. Post-incident actions (2–4 items)
8. Time budget

Sections 1–6 must be under 600 words. Commands must work against the actual Week 10 implementation.

The original assignment describes an Enterprise Knowledge Assistant returning an old parental-leave answer after a policy update. For this capstone, the same incident pattern was adapted to the CBSE corpus. This is a hypothetical CBSE incident, not a claim that a real CBSE production incident occurred.

---

## 1. Inspect the actual implementation before using sample commands

The instructor's sample contains function names and parameters that differ from this project. We inspected the code before adapting the commands.

### 1.1 `src/rag/cache.py`

Important findings:

- SQLite database: `results.db`
- Cache table: `query_cache`
- Similarity threshold: `0.95`
- Timestamp column: `created_ts`
- `cache.stats(db_path)` returns `n_entries` and `total_hits`.
- `cache.clear(db_path)` clears rows from the semantic-cache table and returns the number cleared.
- `cache.lookup(...)` looks for a similar cached question.
- `cache.put(...)` stores a question, embedding and answer.

The cache-clear operation does not delete the Qdrant knowledge base.

### 1.2 `src/rag/qdrant_rag.py`

Important findings:

- Public function: `ask_rag(question, k=3, cache_threshold=0.95)`.
- It calls `cache.lookup(...)`.
- On a cache hit, it returns the stored answer and `cache_hit: True`.
- On a cache miss, it performs retrieval, generates an answer and stores it.
- This implementation does **not** support `use_cache=False`.
- It does **not** accept a `store` argument.

### 1.3 `src/rag/retrieval.py`

Important findings:

- `retrieve(query, k=3)` performs hybrid retrieval followed by reranking.
- `dense_search()` applies a tombstone filter by default.
- `bm25_search()` originally did not apply a tombstone filter.
- `_load_bm25()` originally loaded all Qdrant points.
- `_load_bm25()` uses `@lru_cache(maxsize=1)`, retaining its index within a Python process.

### 1.4 `src/rag/pipeline.py` and `scripts/update_document.py`

The document-update pipeline:
- tombstones old chunks for the source;
- processes and embeds the updated document;
- inserts new chunks;
- clears the semantic cache by default through `cache.clear()` when `clear_cache_after=True`.

The default for `clear_cache_after` is `True`. Therefore, cache clearing already exists in the current update pipeline.

### 1.5 Instructor sample versus actual implementation

| Instructor sample | Actual implementation |
|---|---|
| `clear_cache()` | `cache.clear()` |
| `created_at` | `created_ts` |
| `ask_rag(..., use_cache=False)` | No `use_cache` parameter |
| `ask_rag(question, load_store())` | `ask_rag()` takes the question, not a store |

We retained the assignment's diagnostic intent but used commands matching the actual code.

---

## 2. Diagnostic 1 – Inspect the semantic cache

**Working directory:** `Week10`

```bash
python3 - <<'PY'
import sqlite3
from src.rag import cache

db_path = "./results.db"

print("CACHE STATISTICS")
print(cache.stats(db_path))

print("\nSTORED CBSE QUESTIONS")
conn = sqlite3.connect(db_path)

rows = conn.execute("""
    SELECT question, answer, hit_count, created_ts
    FROM query_cache
    WHERE question LIKE '%CBSE%'
    ORDER BY created_ts DESC
    LIMIT 10
""").fetchall()

for question, answer, hits, created in rows:
    print("\nQuestion:", question)
    print("Answer:", answer)
    print("Hits:", hits)
    print("Created:", created)

conn.close()
PY
```

**Actual output:**

```text
CACHE STATISTICS
{'n_entries': 24, 'total_hits': 1}

STORED CBSE QUESTIONS

Question: What subjects are included in the CBSE Class IX curriculum?
Answer: I don't know.
Hits: 0
Created: 1795603998.66183

Question: What is the CBSE scheme of studies for Class IX for 2026-27?
Answer: I don't know.
Hits: 1
Created: 1795603995.8588278
```

**Interpretation:**

- The cache contained 24 entries.
- Total recorded hits: 1.
- The selected CBSE question was already cached.
- Its stored answer was `I don't know.`

This did not demonstrate a stale-answer incident. The stored answer was not identified as an old answer from a previous CBSE document version. The cache was not cleared yet because investigation was still in progress.

---

## 3. Diagnostic 2 – Inspect live retrieval independently of the semantic cache

`ask_rag()` has no `use_cache=False` option. We therefore used `retrieve()` directly to inspect the live retrieved chunks without using the semantic answer cache.

**Working directory:** `Week10`

```bash
python3 - <<'PY'
from src.rag.retrieval import retrieve

question = "What is the CBSE scheme of studies for Class IX for 2026-27?"

results = retrieve(question, k=3)

for i, item in enumerate(results, start=1):
    doc = item["doc"]
    print(f"\n--- Retrieved chunk {i} ---")
    print("Source:", doc.get("source"))
    print("Deleted at:", doc.get("deleted_at"))
    print("Text:", doc.get("text", "")[:1000])
PY
```

**Actual result:**

- Chunk 1: `Curriculum_SecP1_2026-27.pdf`, `Deleted at: None`
- Chunk 2: `70_Circular_2026.pdf`, `Deleted at: None`
- Chunk 3: `70_Circular_2026.pdf`, a non-empty `deleted_at` timestamp

**Interpretation:** Two chunks were active, but a tombstoned chunk appeared in retrieval. This indicated inconsistent tombstone filtering in hybrid retrieval. It was a separate retrieval issue from semantic-cache staleness.

---

## 4. Diagnostic 3 – Confirm semantic cache-hit behaviour

**Working directory:** `Week10`

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

**Actual output:**

```text
Cache hit: True
Matched question: What is the CBSE scheme of studies for Class IX for 2026-27?
Similarity: 0.9999994413644968
Answer: I don't know.
```

**Interpretation:**

- `cache_hit: True` confirms the answer came from the semantic cache.
- Similarity was almost 1.0.
- The matched question was the same question.
- The cached answer was `I don't know.`

This confirmed cache-hit behaviour, but did not prove that an outdated answer had been returned. The stale-answer incident remained hypothetical for the CBSE adaptation.

---

## 5. Investigate and correct the BM25 tombstone-filter issue

### 5.1 Inspect `bm25_search()`

Command:

```bash
grep -n -A35 -B5 "def bm25_search" src/rag/retrieval.py
```

The function ranked BM25 results and returned the top results without checking `deleted_at`.

### 5.2 Inspect `_load_bm25()`

Command:

```bash
sed -n '55,100p' src/rag/retrieval.py
```

The function used Qdrant `client.scroll()` to load all points. The scroll call had no filter, so it loaded active and tombstoned chunks into the BM25 index. By comparison, `dense_search()` used `_live_filter()` by default.

### 5.3 Apply the tombstone filter

**File edited:** `Week10/src/rag/retrieval.py`

**Action:** Replace only the existing `client.scroll()` call inside `_load_bm25()` with:

```python
batch, next_offset = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=200,
    offset=offset,
    with_payload=True,
    scroll_filter=_live_filter(),
)
```

This makes the BM25 index load only active chunks.

### 5.4 Verify the edit

```bash
sed -n '72,100p' src/rag/retrieval.py
```

The output showed `scroll_filter=_live_filter()` in the Qdrant scroll call.

### 5.5 Re-run retrieval

```bash
python3 - <<'PY'
from src.rag.retrieval import retrieve

question = "What is the CBSE scheme of studies for Class IX for 2026-27?"

results = retrieve(question, k=3)

for i, item in enumerate(results, start=1):
    doc = item["doc"]
    print(f"\n--- Retrieved chunk {i} ---")
    print("Source:", doc.get("source"))
    print("Deleted at:", doc.get("deleted_at"))
    print("Text:", doc.get("text", "")[:500])
PY
```

**Actual result after the change:** All three returned chunks showed `Deleted at: None`. The top three results contained active chunks only.

**Conclusion:** The BM25 tombstone-filter correction worked in this test.

**In-memory index qualification:** `_load_bm25()` uses `@lru_cache(maxsize=1)`. A running Python process can retain an index built before a document update. Separate command-line Python processes start with a fresh in-memory cache, but a continuously running API process may need an explicit index-refresh mechanism after updates. The test above ran in a fresh Python process; it did not verify refresh behaviour in a continuously running API server.

This BM25 correction is a separate technical improvement. It does not replace the assignment's primary stale semantic-cache diagnosis.

---

## 6. Inspect the document-update pipeline

Commands:

```bash
sed -n '1,240p' scripts/update_document.py
```

```bash
sed -n '1,260p' src/rag/pipeline.py
```

The update pipeline showed that it already clears the semantic cache by default:

```python
cache_cleared = (
    cache.clear() if clear_cache_after else 0
)
```

The default value of `clear_cache_after` is `True`.

Therefore, the current project already implements cache clearing during document updates. The post-incident recommendation is to protect this behaviour with regression tests and deployment safeguards, not to claim that cache clearing is absent from the current implementation.

---

## 7. Prepare the incident runbook

**Runbook file:**

```text
Week10/docs/runbooks/wk10_incident_stale_cache.md
```

The runbook follows the assignment's eight required sections.

### 7.1 Section 1 – Title and summary

Title: `Incident: Stale CBSE Answer After Document Update`

The summary explains that the assistant returns an outdated answer from the semantic cache after the source document has been updated.

### 7.2 Section 2 – Symptoms

Five symptoms were documented:

- Users receive answers based on an older document version.
- The same outdated answer is repeatedly returned.
- The document update reports successful tombstoning and ingestion.
- Response metadata indicates a semantic-cache hit.
- Multiple users report the same issue.

These are hypothetical symptoms for the adapted CBSE scenario.

### 7.3 Section 3 – Likely root cause

The root cause paragraph identifies a stale entry in `results.db`, table `query_cache`. A question with similarity at or above the 0.95 threshold can match the stored question and return the old answer without fresh retrieval.

### 7.4 Section 4 – Diagnostic steps

Three diagnostics were included:

1. Confirm a semantic cache hit using `ask_rag()`.
2. Inspect live knowledge-base retrieval using `retrieve()`.
3. Inspect cache statistics and the affected cache row using SQLite.

### 7.5 Section 5 – Fix

Three ordered steps were included:

1. Clear the semantic cache using `cache.clear("./results.db")`.
2. Confirm the cache is empty using `cache.stats("./results.db")`.
3. Re-ask the original question using `ask_rag()` to generate and store a fresh answer.

### 7.6 Section 6 – Verification

Three checks were included:

1. Confirm the first question after clearing the cache has `cache_hit: False` and returns the updated answer.
2. Ask the same question again and confirm `cache_hit: True`.
3. Check cache statistics to confirm the refreshed entry is stored and reused.

### 7.7 Section 7 – Post-incident actions

Four actions were included:

1. Protect cache invalidation during document updates with a regression test or CI check.
2. Require update workflows to verify successful cache clearing.
3. Notify the six affected users and ask them to recheck the answer.
4. Monitor cache-hit rate and investigate sustained rates above 90% for one hour.

### 7.8 Section 8 – Time budget

| Activity | Estimated time |
|---|---:|
| Diagnosis | 8 minutes |
| Fix and cache verification | 3 minutes |
| Post-incident actions and user communication | 15 minutes |
| **Total** | **Approximately 25 minutes** |

---

## 8. Final checks and submission details

The following command was run from the `Week10` directory:

```bash
git diff --check
```

It returned no output, meaning Git reported no whitespace errors in the tracked changes it checked.

**Qualification:** If the new runbook is untracked, `git diff --check` does not inspect it. Check Git status:

```bash
git status --short
```

The assignment specifies this commit-message tag:

```text
W10 activity: stale cache incident runbook
```

Required submission path:

```text
docs/runbooks/wk10_incident_stale_cache.md
```

---

## 9. Important learning points

1. A semantic cache can return an answer without performing fresh retrieval when a sufficiently similar cached question is found.
2. `cache_hit: True` confirms a cache hit, but does not by itself prove that the answer is stale or incorrect.
3. Cache statistics and stored question/answer rows help investigate cache state.
4. `cache.clear()` clears semantic-cache entries; it does not delete the knowledge base.
5. Dense retrieval and BM25 retrieval must apply consistent tombstone rules.
6. An in-memory BM25 index can remain stale inside a long-running process unless refreshed.
7. The document-update pipeline should clear the semantic cache after a successful update.
8. Incident runbooks must use commands that match the actual implementation, not blindly copy sample commands.

## 10. Actual findings versus hypothetical incident assumptions

| Item | Status |
|---|---|
| Cache contained 24 entries | Observed in the project |
| Selected CBSE question was cached | Observed in the project |
| Cached answer was `I don't know.` | Observed in the project |
| `ask_rag()` returned `cache_hit: True` | Observed in the project |
| One tombstoned chunk appeared in retrieval before the BM25 correction | Observed in the project |
| BM25 retrieval returned active chunks after the correction | Observed in the project |
| CBSE production users received an old answer after a document update | Hypothetical assignment scenario |
| Six CBSE users received a stale answer | Adapted from the assignment scenario; not an observed project incident |

The distinction matters: the assignment runbook describes how to respond to the hypothetical incident, while the investigation records what was actually observed in the CBSE capstone project.
