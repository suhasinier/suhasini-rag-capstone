# Week 7 KPI Snapshot — Qdrant Migration

**Date:** 2026-10-23  
**Vector store:** Qdrant Cloud  
**Collection:** `capstone_chunks`  
**Points migrated:** 415  
**Vector dimensions:** 1536  
**Embedding model:** `text-embedding-3-small`

## Headline numbers

| Metric | Week 6 (JSON) | Week 7 (Qdrant) | Difference |
|---|---|---|---|
| Cost per query | Not measured | $0.00016514 average | Newly measured |
| Latency p50 (ms) | Not measured | 2111.01 | Newly measured |
| Latency p95 (ms) | Not measured | 5056.23 | Newly measured |
| Retrieval hit rate | 100% (18/18 in-corpus questions) | 100% (18/18 in-corpus questions) | 0 percentage points |
| Grounded response rate | Not measured | Pending evaluation | Pending |

**Important:** Both retrieval hit rates use the same 20-question CBSE Class 9 evaluation set, with 18 in-corpus questions scored and 2 out-of-corpus questions excluded from the retrieval hit-rate calculation. The hit-rate metric checks whether at least one expected source appears among the top 3 retrieved results. It does not measure answer correctness or abstention quality.

## Operational comparison

| Property | Week 6 | Week 7 |
|---|---|---|
| Persistence | JSON file | Qdrant Cloud |
| Vector retrieval | NumPy linear scan | Qdrant search |
| Metadata filtering | Not available in the original design | Prepared for future filtering |
| Scaling | In-memory vectors | Qdrant-managed vectors |

## Verification completed

- Migrated 415 embedding records from `Week6/data/embeddings_large.json`.
- Confirmed the Qdrant collection `capstone_chunks` contains 415 points.
- Confirmed the FastAPI health endpoint returns `{"status":"ok"}`.
- Successfully tested `/ask_batched` with a curriculum question about learner-centred teaching and assessment.
- The API response included an answer, source IDs, chunk IDs, and token counts.
- Evaluated Qdrant retrieval using `Week6/data/golden_set_cbse_class9_wk6_14-4-2.jsonl`.
- Confirmed 20 evaluation records: 18 in-corpus questions scored, with 18 hits (100.00%); 2 out-of-corpus questions remain unscored for separate abstention testing.
- Saved the evaluation records to `Week7/data/eval/qdrant.json`.
- Matched the Week 6 large-chunk baseline retrieval hit rate of 100.00% on the same evaluation set.


## Method

- Use the 20-question CBSE Class 9 evaluation set from `Week6/data/golden_set_cbse_class9_wk6_14-4-2.jsonl`.
- Use the Week 6 large-chunk baseline for comparison.
- Run the evaluation against the Week 7 Qdrant pipeline.
- Record retrieval hit rate using the same source-match criteria: at least one expected source among the top 3 retrieved results.
- Exclude the 2 out-of-corpus questions from retrieval hit-rate calculation; evaluate abstention separately.
- Measure grounded response rate, latency, and cost only when the required evaluation data is available.


## Embedding-model comparison

| Metric | text-embedding-3-small | text-embedding-3-large |
|---|---:|---:|
| Embedding dimensions | 1536 | 3072 |
| Corpus chunks indexed | 415 | 415 |
| In-corpus questions scored | 18 | 18 |
| Retrieval hits | 18 | 17 |
| Retrieval hit rate | 100.00% | 94.44% |

- Evaluation dataset: `Week6/data/golden_set_cbse_class9_wk6_14-4-2.jsonl`
- Small-model results: `Week7/data/eval/qdrant.json`
- Large-model results: `Week7/data/eval/qdrant_large.json`
- The large model missed question `g003` about when a foreign language may be offered in the revised language scheme.
- The small model retrieved the expected source, `33_Circular_2026.pdf`; the large model did not retrieve that source in its top 3 results.
- The two out-of-corpus questions, `g019` and `g020`, were excluded from the retrieval hit-rate calculation. Abstention quality has not yet been measured.
- Current evidence favors `text-embedding-3-small` for this corpus because it achieved the higher retrieval hit rate. The final choice should also consider cost and latency.

## Cost and latency benchmark

- Evaluation dataset: `Week6/data/golden_set_cbse_class9_wk6_14-4-2.jsonl`
- Questions measured: 20
- Embedding model: `text-embedding-3-small`
- Chat model: `gpt-4o-mini`
- Vector store: Qdrant Cloud, collection `capstone_chunks`
- Top-k retrieval: 3
- Median end-to-end latency (p50): 2111.01 ms
- 95th-percentile end-to-end latency (p95): 5056.23 ms
- Average cost per query: $0.00016514
- Total benchmark cost: $0.00330283
- Detailed results: `Week7/data/eval/qdrant_cost_latency.json`

Cost figures use the token prices configured in the benchmark script.
Latency reflects a single run of 20 questions and may vary between runs.

## Grounded response quality review

- Evaluation set: 20 questions
- In-corpus questions reviewed: 18
- Out-of-corpus questions: 2
- Retrieval hit rate: 100% (18/18)
- Correct abstentions: 2/2, based on the current review
- Answers with identified quality issues: 4 (g001, g008, g013, g017)
- Estimated grounded-response rate: **77.78% (14/18)**

### Observations

The retriever found at least one expected source in the top three results for all 18 in-corpus questions. However, four answers had identified quality issues involving missing details or insufficiently specific explanations.

The grounded-response rate of 77.78% is a preliminary estimate based on the current answer-quality review. It assumes the four flagged answers do not pass the current acceptance criteria; it is not a formally validated grounding score.

Answer quality may be affected by embedding-model selection, chunk size and content, retrieval quality, and how the language model uses the retrieved context. Further evaluation is needed to determine the contribution of each factor.

Future improvements to retrieval, chunking, and answer generation may improve this rate. The current estimate will serve as a baseline for comparison in subsequent weeks.