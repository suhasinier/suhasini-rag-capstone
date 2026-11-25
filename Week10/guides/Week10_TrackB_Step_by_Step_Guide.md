# Week 10 Track B — Step-by-Step Implementation Guide
## Core activities + Stretch B: Cold-start cache priming

**Project:** `suhasini-rag-capstone`  
**Working directory:** `Week10`  
**Environment:** Vocareum VS Code terminal, Python 3.10.14  
**Completion date:** 25 November 2026

This guide records the implementation work completed in Week 10 Track B, including commands, purposes, validation results, and issues encountered. The original Week 10 Application Growth Guide remains the source of truth for activity requirements.

## 1. Week 10 overview

Week 10 Track B extended the RAG application with:
1. A SQLite semantic cache.
2. Document update lifecycle support using tombstones and re-ingestion.
3. Cache performance measurement.
4. Operational documentation and a knowledge-base changelog.
5. Stretch B: pre-populating the cache with synthetic question-and-answer queries.

Start from the project directory:

```bash
cd ~/suhasini-rag-capstone/Week10
```

The work reused the Week 8 ingestion helpers and Week 9 retrieval pipeline.

## 2. Step 1 — Implement the semantic cache

### Purpose

A semantic cache stores a question, its embedding, and the answer returned by the RAG system. If a later question is sufficiently similar to a stored question, the application can reuse the cached answer instead of repeating the full retrieval and generation process.

Implementation file:

```text
src/rag/cache.py
```

The module uses SQLite and provides:
- `lookup(...)` — searches for a sufficiently similar cached question.
- `put(...)` — stores a question, embedding, and answer.
- `clear(...)` — removes cache entries.
- `stats(...)` — reports the number of entries and accumulated cache hits.

The configured default similarity threshold is `0.95`.

### Preserve the Week 2 database

The Week 2 SQLite database was copied into the Week 10 directory to give Week 10 its own database file. Run from `Week10`:

```bash
cp ../Week2/results.db ./results.db
```

The copied file was checked against the Week 2 source using SHA-256. Matching hash:

```text
de184131829008aeeb67e56f1760523a490b8b800dce7196027dfb061f50ead9
```

### Connect the cache to the RAG application

The cache-first logic was wired into:

```text
src/rag/qdrant_rag.py
```

The flow is:
1. Receive a user question.
2. Create its embedding.
3. Check the semantic cache.
4. If a sufficiently similar cached question is found, return its stored answer.
5. Otherwise, continue with retrieval and answer generation.
6. Store the new question, embedding, and answer in the cache.

### Validate the cache-first flow

The cache was cleared before the first query. The same question was submitted twice:

```text
what is the leave policy?
```

Observed behaviour:
- First request: cache miss; the RAG pipeline ran.
- Second request: cache hit with similarity `1.0`; the cached answer was reused.

The answer was `"I don't know."` because the corpus did not contain the requested leave-policy information. This was a corpus-coverage result, not a cache failure.

Syntax validation:

```bash
python -m py_compile src/rag/cache.py src/rag/qdrant_rag.py
```

The command completed successfully.

## 3. Prepare the Week 10 document corpus

The Week 8 corpus was copied into the Week 10 `data/corpus/` folder. The corpus was extended with the official CBSE circular used for the document-update exercise.

Download command:

```bash
wget -O data/corpus/70_Circular_2026.pdf https://cbseacademic.nic.in/web_material/Circulars/2026/70_Circular_2026.pdf
```

The circular was CBSE Academic Circular Acad-70/2026, titled *Scheme of Studies for Class IX 2026-27*, dated 29 October 2026.

Week 8 ingestion helpers were copied into:

```text
src/ingest/
    __init__.py
    chunkers.py
    pii.py
    pipeline.py
```

The supporting `wk08_pipeline.py` file was also copied because the lifecycle pipeline uses its `chunk_recursive` helper.

PyMuPDF, Presidio packages, and the spaCy `en_core_web_lg` model were installed because they were required by the copied ingestion helpers.

## 4. Step 2 — Implement document lifecycle and tombstones

### Purpose

When a source document is updated, the knowledge base must stop treating the old chunks as current. The old chunks are retained for audit purposes but marked as deleted. New chunks are then ingested.

This is called **tombstoning**:
- Old points remain in Qdrant.
- A `deleted_at` payload field marks them as no longer live.
- Normal retrieval filters out tombstoned points.
- An audit query can explicitly include deleted points.

### Qdrant payload indexes

The following payload indexes were created:
- `source` — keyword index.
- `deleted_at` — float index.

These fields support filtering by source document and tombstone status.

### Lifecycle pipeline

Implementation file:

```text
src/rag/pipeline.py
```

The module contains:
- `KB_VERSION = "2"`
- `tombstone_source(store, source)`
- `ingest_or_update_source(store, source, body, doc_type="pdf", clear_cache_after=True)`

`tombstone_source(...)`:
1. Builds a filter for the requested source.
2. Restricts the filter to records whose `deleted_at` field is empty.
3. Counts those live records.
4. Sets `deleted_at` on the matching points.
5. Returns the number of records tombstoned.

`ingest_or_update_source(...)`:
1. Tombstones the old live chunks for the source.
2. Splits the new document body into chunks.
3. Scrubs the chunks using the Week 8 PII helper.
4. Enriches each chunk with metadata.
5. Adds the knowledge-base version.
6. Creates embeddings.
7. Upserts the new points into Qdrant.
8. Clears the semantic cache when requested.
9. Returns counts for tombstoned chunks, ingested chunks, and cleared cache entries.

### Live-record retrieval filter

The retrieval logic was implemented in:

```text
src/rag/retrieval.py
```

The normal search path applies a live-record filter using Qdrant's `IsEmptyCondition` on `deleted_at`. The search function also supports `include_deleted=True` for audit use; this bypasses the normal live-only restriction.

### Document update script

Created:

```text
scripts/update_document.py
```

The script accepts a PDF path, checks that the file exists, extracts its text using PyMuPDF, uses the PDF filename as the source identifier, loads the Qdrant store, calls `ingest_or_update_source(...)`, and prints the tombstoned, ingested, and cache-cleared counts.

Run from `Week10`:

```bash
python -m scripts.update_document data/corpus/70_Circular_2026.pdf
```

### Validate the update operation

First update run:

```text
Tombstoned: 0 old chunks
Ingested:   59 new chunks
Cache cleared: 1 entries
```

Second update run on the same PDF:

```text
Tombstoned: 59 old chunks
Ingested:   59 new chunks
Cache cleared: 0 entries
```

The second run demonstrated that the previous live chunks were tombstoned before replacement chunks were ingested.

### Validate normal retrieval and audit retrieval

The Qdrant checks showed:
- Total circular chunks: `118`
- Live circular chunks: `59`
- Tombstoned circular chunks: `59`
- Normal search returned circular chunks with `0` deleted records.
- An audit search with `include_deleted=True` returned deleted records as well; one audit result contained 56 circular chunks, of which 28 were deleted.

The audit query is a search query, not a full collection scroll, so it is not expected to return every point in the collection. The important check was that normal retrieval excluded deleted chunks and audit retrieval could include them.

Syntax and import checks:

```bash
python -m py_compile src/rag/pipeline.py
python -m py_compile scripts/update_document.py
```

Both syntax checks completed successfully. The Week 8 helper imports and update-script import check also succeeded.

## 5. Step 3 — Measure Week 10 cache performance

### Prepare the golden question set

The Week 9 golden set was copied into:

```text
data/golden_set.jsonl
```

It contained 20 records.

The `ask_rag` function used for evaluation had this interface:

```python
ask_rag(
    question: str,
    k: int = 3,
    cache_threshold: float = 0.95
) -> dict[str, Any]
```

### Create and run the measurement script

Created:

```text
scripts/measure_wk10_cache.py
```

The script measures a cold pass and a warm pass over the golden questions. The warm pass repeats the questions so that the cache can serve them.

Run from `Week10`:

```bash
python -m scripts.measure_wk10_cache
```

Recorded results:

| Metric | Cold pass | Warm pass |
|---|---:|---:|
| Cache hits | 0 | 20 |
| p50 latency | 3066 ms | 507 ms |
| p95 latency | 66245 ms | 598 ms |
| Estimated total cost | $0.00129 | $0.00001 |

The estimated warm-pass cost saving was **99.5%**.

### Measurement limitations

- Cost is an estimate based on the pricing assumptions used in the guide; it is not a measurement of actual billing.
- Question embedding tokens were estimated using `len(question.split())`, not a tokenizer.
- Precision and groundedness were not re-measured in this Week 10 evaluation.
- A Hugging Face authentication warning appeared during execution but did not prevent the evaluation from completing.

The results and limitations were recorded in:

```text
docs/kpi/wk10-snapshot.md
```

The snapshot also records the prior Week 9 precision values: Precision@3 `0.556` and Precision@5 `0.778`. Week 10 precision and groundedness are marked as not measured rather than assuming that Week 9 values still apply.

## 6. Step 4 — Documentation and operational runbook

### Preserve the Architecture Decision Record

The Week 10 ADR folder did not initially contain the existing project ADR. The Week 9 ADR was copied into Week 10:

```bash
mkdir -p docs/adr
cp ../Week9/docs/adr/0001-capstone-framing.md docs/adr/0001-capstone-framing.md
```

The Week 10 section was appended to:

```text
docs/adr/0001-capstone-framing.md
```

The earlier W1–W9 history was retained.

### Document-update runbook

Created:

```text
docs/runbooks/document_update.md
```

The runbook describes the document update procedure and checks to perform after an update.

**Rollback caution:** capture the old and new point IDs when planning a rollback. Do not delete chunks using only the source name, because that could remove both old and current versions.

### Knowledge-base changelog

Created:

```text
docs/kb-changelog.md
```

It records the circular update runs:

| Run | Old chunks tombstoned | New chunks ingested | Cache entries cleared |
|---|---:|---:|---:|
| First ingestion | 0 | 59 | 1 |
| Re-ingestion test | 59 | 59 | 0 |

The documentation files were checked by displaying their contents in the terminal.

## 7. Step 5 — Stretch B: Cold-start synthetic Q+A cache priming

### Purpose

A newly started application may have an empty semantic cache. Cold-start priming sends a prepared set of representative questions through the RAG pipeline before normal users begin asking questions.

The first run stores the resulting question embeddings and answers. A later identical or sufficiently similar question can then be served from the cache.

### Record and clear the initial cache state

Before priming:

```text
{'n_entries': 20, 'total_hits': 20}
```

The cache was cleared to create a cold-start condition:

```text
Cleared: 20
{'n_entries': 0, 'total_hits': 0}
```

### Create and run the priming script

Created:

```text
scripts/cold_start_prime.py
```

It contains 24 prepared questions based on the CBSE corpus, covering curriculum and scheme of studies, Mathematics, Science, Social Science, English, and CBSE Circular 70/2026. Each question is sent through `ask_rag(...)`.

Run from `Week10`:

```bash
python -m scripts.cold_start_prime
```

All 24 questions completed. Each first-run result showed `hit=False`, which is expected because the questions were first-time requests and were populating the empty cache. A Hugging Face authentication warning appeared but did not stop the script.

After priming:

```text
{'n_entries': 24, 'total_hits': 0}
```

An identical repeat question was submitted:

```text
What is the CBSE scheme of studies for Class IX for 2026-27?
```

Observed result:

```text
Cache hit: True
Similarity: 1.0
```

This confirms that the matching primed question could be served from the cache.

The implementation and observations were documented in:

```text
docs/wk10-stretch-notes.md
```

The recorded recommendation was **KEEP**, with limitations. The 24 entries demonstrate that priming populated the cache and that an identical repeat could hit it. The run did not establish real first-week production savings or measure answer groundedness.

## 8. Create and run the missing test files

During the final checklist audit, two required files were found to be missing:

```text
tests/test_cache.py
tests/test_tombstones.py
```

The `tests` directory was created from the Week 10 terminal:

```bash
mkdir -p tests
ls -la tests/
```

### Install pytest for the active interpreter

The first test attempt used `python -m pytest` and returned:

```text
/usr/bin/python: No module named pytest
```

Pytest was then installed for the active Python 3 interpreter:

```bash
python3 -m pip install --user pytest
```

Use `python3` consistently for the test commands in this environment.

### Cache tests

`tests/test_cache.py` contains four tests:
1. An empty cache lookup returns `None`.
2. A stored question and answer can be retrieved.
3. A question below the similarity threshold is rejected.
4. Cache statistics and clearing behave as expected.

Run:

```bash
python3 -m pytest tests/test_cache.py -v
```

Observed result:

```text
4 passed in 0.48s
```

### Tombstone tests

`tests/test_tombstones.py` contains two tests:
1. `tombstone_source()` counts live chunks for the requested source and sets `deleted_at` on matching records. A fake Qdrant client is used so the test does not modify the real collection.
2. The normal live-record filter contains the `IsEmptyCondition` required to exclude tombstoned chunks.

Run:

```bash
python3 -m pytest tests/test_tombstones.py -v
```

Observed result:

```text
2 passed
```

### Run the complete test folder

Run:

```bash
python3 -m pytest tests/ -v
```

Final observed result:

```text
collected 6 items

tests/test_cache.py::test_lookup_returns_none_for_empty_cache PASSED
tests/test_cache.py::test_put_and_lookup_returns_cached_answer PASSED
tests/test_cache.py::test_lookup_rejects_question_below_similarity_threshold PASSED
tests/test_cache.py::test_stats_and_clear PASSED
tests/test_tombstones.py::test_tombstone_source_marks_only_live_chunks_of_source PASSED
tests/test_tombstones.py::test_live_filter_excludes_tombstoned_chunks PASSED

6 passed in 3.47s
```

## 9. Final Week 10 file inventory

The final inventory command was run from the `Week10` directory:

```bash
for f in \
tests/test_cache.py \
tests/test_tombstones.py \
src/rag/cache.py \
src/rag/qdrant_rag.py \
src/rag/pipeline.py \
src/rag/retrieval.py \
scripts/update_document.py \
scripts/measure_wk10_cache.py \
scripts/cold_start_prime.py \
docs/kpi/wk10-snapshot.md \
docs/adr/0001-capstone-framing.md \
docs/runbooks/document_update.md \
docs/kb-changelog.md \
docs/wk10-stretch-notes.md
do
    if [ -f "$f" ]; then
        echo "FOUND   $f"
    else
        echo "MISSING $f"
    fi
done
```

All 14 checked files were reported as `FOUND`.

| Area | Required file | Final check |
|---|---|---|
| Cache tests | `tests/test_cache.py` | Found; 4 tests passed |
| Tombstone tests | `tests/test_tombstones.py` | Found; 2 tests passed |
| Cache | `src/rag/cache.py` | Found |
| Cache-first RAG | `src/rag/qdrant_rag.py` | Found |
| Lifecycle pipeline | `src/rag/pipeline.py` | Found |
| Retrieval | `src/rag/retrieval.py` | Found |
| Document update | `scripts/update_document.py` | Found |
| Cache measurement | `scripts/measure_wk10_cache.py` | Found |
| Stretch B priming | `scripts/cold_start_prime.py` | Found |
| KPI snapshot | `docs/kpi/wk10-snapshot.md` | Found |
| ADR | `docs/adr/0001-capstone-framing.md` | Found |
| Runbook | `docs/runbooks/document_update.md` | Found |
| KB changelog | `docs/kb-changelog.md` | Found |
| Stretch notes | `docs/wk10-stretch-notes.md` | Found |

## 10. Completion summary

| Week 10 activity | Status |
|---|---|
| Step 1 — Semantic cache | Completed and manually validated |
| Step 2 — Document lifecycle and tombstones | Completed and manually validated |
| Step 3 — Cache KPI measurement | Completed; results recorded with caveats |
| Step 4 — ADR, runbook, and changelog | Completed |
| Stretch B — Cold-start cache priming | Completed and repeat-hit verified |
| Cache unit tests | 4 passed |
| Tombstone unit tests | 2 passed |
| Combined test suite | 6 passed |
| Final file inventory | 14 of 14 found |

**Week 10 Track B (Core + Stretch B) is complete based on the implementation, validation, and file checks recorded above.**

The checks performed do not constitute a complete production-readiness or end-to-end test of every possible scenario. In particular, the cost figures are estimates, and Week 10 precision and groundedness were not re-measured. Those limitations are recorded rather than treated as successful measurements.
