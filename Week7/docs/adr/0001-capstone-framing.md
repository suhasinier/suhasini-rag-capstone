
# W7 — Qdrant-backed vector store

## Decision

The capstone will use Qdrant Cloud as its vector store. The existing
naive_rag.py implementation will be retained as a reference.

## Vector stack

- Embedding model: text-embedding-3-small
- Embedding dimensions: 1536
- Vector store: Qdrant Cloud
- Distance metric: cosine
- Index: HNSW with default configuration


## Alternatives considered

- **text-embedding-3-large:** Evaluated against the same 20-question CBSE Class 9 golden set. It achieved 17/18 (94.44%) in-corpus retrieval hits, compared with 18/18 (100%) for `text-embedding-3-small`. The larger model did not improve retrieval hit rate on this evaluation set.
- **FAISS:** An alternative vector-search library that does not provide the same managed service layer as the selected design.
- **Chroma:** An alternative vector store.
- **pgvector:** An alternative requiring PostgreSQL in the current stack.


## Operational changes

- Vector persistence moves from a JSON cache to Qdrant.
- Qdrant manages vector search.
- Metadata payloads prepare the system for filtering in Week 8.
- Performance and retrieval quality will be recorded in docs/kpi/wk7-snapshot.md.

## Validation

- Migrated 415 embedding records from the Week 6 large-chunk index into the Qdrant Cloud collection `capstone_chunks`.
- Confirmed the collection contains 415 points with 1536-dimensional vectors.
- Confirmed the FastAPI health endpoint and tested the `/ask_batched` endpoint successfully.
- Evaluated retrieval using the 20-question CBSE Class 9 dataset: `Week6/data/golden_set_cbse_class9_wk6_14-4-2.jsonl`.
- Week 6 JSON retrieval baseline: 18/18 in-corpus questions matched an expected source (100%).
- Week 7 Qdrant retrieval: 18/18 in-corpus questions matched an expected source (100%).
- Cost and latency were measured in a 20-question evaluation run. The estimated grounded-response rate is 77.78% (14/18), based on the preliminary answer-quality review documented in the Week 7 KPI snapshot.
- Compared `text-embedding-3-small` and `text-embedding-3-large` using the same CBSE Class 9 golden set and top-3 source-match criteria.
- Small model: 18/18 in-corpus retrieval hits (100%); large model: 17/18 (94.44%).
- The large model missed g003, a question about when a foreign language may be offered in the revised language scheme. The small model retrieved the expected source, `33_Circular_2026.pdf`; the large model did not.
- Decision: retain `text-embedding-3-small` for the current capstone because it achieved the higher measured retrieval hit rate on this dataset. Cost and latency have not yet been compared.
- The two out-of-corpus questions were reviewed; both were judged to be correct abstentions in the current review.

