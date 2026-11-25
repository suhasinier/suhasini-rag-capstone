
# wk10-snapshot.md — Caching + lifecycle baseline

**Date:** 2026-11-25

**Stack (W10):** Hybrid retrieval + reranking (W9) + semantic cache (0.95 threshold, SQLite)

**Update flow:** Tombstone (IsEmptyCondition) → insert new chunks → clear semantic cache

## Headline numbers

| Metric | W9 baseline | W10 cold | W10 warm | Observation |
|---|---:|---:|---:|---|
| Precision@3 | 0.556 | Not re-measured | Not re-measured | Cache evaluation did not measure retrieval precision |
| Precision@5 | 0.778 | Not re-measured | Not re-measured | Cache evaluation did not measure retrieval precision |
| Grounded response rate | Not measured | Not measured | Not measured | Not evaluated in W10 |
| Total estimated cost | Not measured | $0.00129 | $0.00001 | 99.5% estimated warm-pass saving |
| Latency p50 | Not measured | 3,066 ms | 507 ms | Warm pass was faster |
| Latency p95 | Not measured | 66,245 ms | 598 ms | Warm pass was faster |
| Cache hit rate | Not measured | 0% | 100% | 20 questions in each pass |

## Method

- Same 20 golden-set questions copied from Week 9.
- Pass 1 (cold): `cache.clear()` before evaluation; all 20 questions went through the full RAG pipeline.
- Pass 2 (warm): same questions repeated immediately; all 20 returned semantic cache hits.
- Cost estimated using the pricing assumptions in the W10 guide.
- Embedding token count estimated using `len(question.split())`, as implemented in the measurement script.
- Latency measured around each `ask_rag()` call.
- W9 precision values taken from the Week 9 evaluation record.

## What changed structurally

- W9 used hybrid retrieval, BM25 + dense search, RRF and cross-encoder reranking.
- W10 added a SQLite-backed semantic cache with a cosine similarity threshold of 0.95.
- Cache lookup happens before the full RAG pipeline.
- Document updates use tombstoning with `IsEmptyCondition`, followed by re-ingestion and cache clearing.
- `dense_search()` excludes tombstoned chunks by default. `include_deleted=True` allows historical retrieval.

## Interpretation

- The cold pass recorded 20 cache misses; the warm pass recorded 20 cache hits.
- Estimated warm-pass cost decreased by 99.5%.
- Median latency decreased from 3,066 ms to 507 ms.
- The warm-pass p95 latency was 598 ms, compared with 66,245 ms in the cold pass.
- These results demonstrate the benefit of semantic caching for this repeated 20-question workload.
- The evaluation does not establish a new precision or grounded-response score for W10.

## Known risks

- False semantic cache hits may return an answer to a similar but different question.
- Cache invalidation must run after document updates to prevent stale answers.
- Cost figures are estimates, not actual billing records.
- The embedding token estimate uses whitespace-separated word count rather than an exact tokenizer.
- Cache performance on this repeated golden set may differ from real-world traffic with more varied questions.
