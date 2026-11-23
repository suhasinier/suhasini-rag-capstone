
## W9 — Hybrid retrieval + cross-encoder reranking

**Decision:** The capstone retrieval implementation was upgraded from W8's pure dense retrieval to a hybrid retrieval and reranking pipeline.

**Retrieval stack:**
- BM25 library: rank-bm25 (BM25Okapi).
- Tokenization: lowercase text with alphanumeric characters, hyphens, slashes and underscores preserved according to the implementation's regular expression.
- Dense model: text-embedding-3-small (1536 dimensions).
- Vector store: Qdrant Cloud, collection capstone_chunks_v2.
- Fusion: Reciprocal Rank Fusion (RRF), k=60.
- Reranker: cross-encoder/ms-marco-MiniLM-L-6-v2.
- Hybrid retrieval produces up to 10 candidates.
- Cross-encoder reranking returns the final top 3 results.

**Alternatives not selected:**
- Cohere Rerank API: not used; the implemented solution uses a local cross-encoder.
- Weighted score fusion: not used; RRF combines the ranked lists.
- Larger cross-encoder: not used; the current implementation uses MiniLM-L-6-v2.
- LlamaIndex: not introduced; the retrieval pipeline is implemented directly in the existing project structure.

**Operational KPIs:**

See `docs/kpi/wk9-snapshot.md`.

The W9 evaluation produced:
- Precision@3: 55.6%, compared with 66.7% for W8.
- Precision@5: 77.8%, compared with 83.3% for W8.

The evaluation therefore shows a decrease in both precision measures. Cost per query, latency p50 and grounded response rate have not yet been measured for W9.

**Known gaps to revisit:**
- The W9 evaluation did not improve precision over the W8 dense-only baseline.
- Questions g004 and g018 became top-3 retrieval misses.
- Out-of-corpus abstention behaviour for g019 and g020 has not been evaluated.
- The BM25 index is built from the Qdrant collection when the retrieval module loads.
- The cross-encoder performs local reranking; its latency has not been benchmarked for this capstone.

These findings should guide future retrieval improvements and evaluation.
