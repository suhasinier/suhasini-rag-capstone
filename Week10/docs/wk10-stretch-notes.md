# Week 10 Stretch Notes — Cold-Start Synthetic Q+A Cache Primer

**Activity:** Stretch B — Cold-start synthetic Q+A cache primer  
**Date:** 2026-11-25

## 1. Objective

Pre-populate the SQLite semantic cache with FAQ-style questions based on the capstone knowledge base before normal user traffic begins.

The purpose is to reduce repeated full RAG pipeline executions when users ask the same or sufficiently similar questions.

## 2. Implementation

Created:

`scripts/cold_start_prime.py`

The script contains 24 hand-crafted questions covering:

- Overall CBSE curriculum and scheme of studies
- Class IX Mathematics
- Class IX Science
- Class IX Social Science
- Class IX English
- CBSE Circular 70/2026

Each question is passed to `ask_rag()`. On a cache miss, the complete RAG pipeline runs and the resulting answer is stored in the semantic cache.

## 3. Results

### Before priming

| Metric | Result |
|---|---:|
| Cache entries | 0 |
| Total cache hits | 0 |

### Priming run

| Metric | Result |
|---|---:|
| Questions processed | 24 |
| Initial cache hits | 0 |
| Initial cache misses | 24 |
| Script execution | Successful |

All 24 questions returned `cache_hit=False` during the first run, as expected with an empty cache.

### After priming

| Metric | Result |
|---|---:|
| Cache entries | 24 |
| Total cache hits at verification time | 0 |

### Repeat-query verification

Repeated this question:

"What is the CBSE scheme of studies for Class IX for 2026-27?"

Observed:

- Cache hit: `True`
- Similarity: `1.0`

This confirms that the question was cached and that an identical repeat query retrieved the cached result.

## 4. Interpretation

The cold-start primer successfully populated the semantic cache with 24 FAQ-style questions.

The repeat-query test demonstrated that an identical question can reuse its cached answer instead of executing the full RAG pipeline again.

This is useful when a knowledge base has predictable, frequently asked questions. Priming the cache before user traffic can reduce the number of full RAG executions for questions that match the prepared entries.

## 5. Limitations

- Only 24 hand-crafted questions were tested.
- The evaluation used the same capstone corpus and a limited set of questions.
- We verified an identical repeat query; we did not measure cache hits for semantically similar but differently worded questions.
- We did not measure actual first-week cost savings or production latency.
- We did not independently evaluate the correctness or groundedness of all 24 cached answers.
- The results do not establish how well the primer will perform with varied real-world user questions.

## 6. Verdict

**KEEP — with limitations.**

The cold-start primer worked as intended: it populated 24 cache entries, and an identical repeat query produced a cache hit with similarity 1.0.

Keep this approach as an optional preparation step when the likely FAQ questions are known in advance.

Before using it in production, evaluate answer quality, semantic-match behaviour, cache hit rate on real traffic, and actual cost savings.