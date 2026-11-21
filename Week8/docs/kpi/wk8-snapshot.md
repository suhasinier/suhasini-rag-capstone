# wk8-snapshot.md — Post-ingestion baseline

**Date:** 2026-11-22  
**Vector store:** Qdrant Cloud  
**Collection:** capstone_chunks_v2 (746 points, 1536 dim, cosine)  
**Chunking strategy:** Recursive (max_size=400)  
**PII scrubbing:** Regex + Presidio hybrid

## Headline numbers

| Metric | W7 (capstone_chunks) | W8 (capstone_chunks_v2) | Delta |
|---|---|---|---|
| Cost per query | $0.00016514 | $0.00011163 | -32.4% |
| Latency p50 (ms) | 2111.01 | 2222.69 | +5.3% |
| Retrieval hit rate | 100% (18/18) | 88.89% (16/18) | -11.11 pp |
| Grounded response rate | 77.78% (14/18, preliminary) | Pending measurement | Pending |
| PII redactions | 0 | 873 redactions | New capability |

**Additional Week 8 latency measurement:**
- Latency p95: 3943.29 ms
- Questions measured: 20
- Total benchmark API cost: $0.00223258
- Benchmark output: `data/eval/qdrant_cost_latency.json`
- Models: `text-embedding-3-small` and `gpt-4o-mini`

## Operational deltas

| Property | W7 | W8 |
|---|---|---|
| Metadata fields per chunk | 3 | 9 |
| Filtered retrieval possible | no | yes |
| PII risk | leak-prone | scrubbed at ingest |

## Method

- Same 20 golden-set questions from W5.
- W7 baseline from Week7/docs/kpi/wk7-snapshot.md.
- W8 evaluation performed against capstone_chunks_v2.
- Retrieval method: top 3 chunks (k=3).
- In-corpus evaluation: 18 questions.
- Out-of-corpus questions: 2 (abstention testing not measured by this retrieval script).
- Hit criterion: at least one expected source appears in the top 3 retrieved chunks.

## Interpretation

Week 8 increased the collection size from 415 to 746 points through the new ingestion pipeline. However, retrieval hit rate decreased from 100% to 88.89%, a reduction of 11.11 percentage points.

Two questions were missed:

1. g006 — What prescribed English textbook is listed for Class IX?
   - Expected source: English_LL_SecP1IX_2026-27.pdf
   - Expected source ranked 6th in the top-10 diagnostic.
   - Relevant textbook information was present in chunk #86.

2. g014 — How does the Class IX Science syllabus divide assessment between theory and internal assessment?
   - Expected source: ScienceSt_SecP1_2026-27.pdf
   - Expected source ranked 4th in the top-10 diagnostic.
   - Relevant information was present in chunks #58 and #60.

Both expected documents and their relevant information were successfully parsed and stored in Qdrant. The misses indicate a retrieval-ranking issue under the top-3 evaluation criterion. Similar information in other documents received higher similarity scores.

The diagnostic suggests that chunking and semantic ranking may contribute to the misses, but the root cause has not yet been established.

Week 8 also introduces PII scrubbing at ingestion, with 873 redactions recorded across the corpus.

Grounded response rate has not yet been formally measured for Week 8 and is intentionally left pending rather than estimated. Query cost and latency have been measured and are reported above.