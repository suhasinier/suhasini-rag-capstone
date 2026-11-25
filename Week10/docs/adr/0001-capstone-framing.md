
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


## W8 — Structure-aware ingestion + PII discipline

**Decision:** The capstone corpus is now ingested via
`src/ingest/pipeline.py`, which parses documents by extension, chunks
recursively (structure-aware where possible), scrubs PII using regex +
Presidio, enriches chunks with the metadata schema, and upserts them to
`capstone_chunks_v2`.

**Ingestion pipeline steps:**

1. Parse documents according to file type.
2. Chunk recursively (maximum chunk size: 400).
3. Scrub PII using regex + Presidio.
4. Enrich metadata.
5. Generate embeddings using `text-embedding-3-small`.
6. Upsert into Qdrant collection `capstone_chunks_v2`.

**PII detection:**

- Regex patterns detect EMAIL, PHONE and EMP_ID.
- Presidio detects PERSON, LOCATION and ORGANIZATION.
- A sample audit of 10 stored chunks is documented in `docs/wk8-pii-audit-sample.md`.
- The audit findings are recorded in `docs/wk8-pii-audit.md`.

**Known gaps identified during stress testing:**

- Obfuscated email formats were missed.
- Several international phone numbers were only partially redacted.
- Spelled-out phone numbers were missed.
- Custom employee ID formats were missed.
- An employee badge was incorrectly classified as a US driver's licence.
- Address components were not consistently removed.
- An IBAN was partially redacted and incorrectly classified as a phone number.
- A masked card number was missed in the first run.

The proposed improvements to employee ID patterns, email normalisation and phone-number detection have not yet been integrated into the main `scrub_chunks()` function. IBAN and masked-card patterns were independently tested successfully but have not yet been integrated.

**Data residency:**

- Embeddings computed by: OpenAI API (US).
- Vectors stored at: Qdrant Cloud (`eu-central-1`).
- LLM inference at: OpenAI API (US).
- Application layer: running inside the Vocareum environment; no separate deployment region confirmed.

**Rejected alternatives:**

- Structure-aware chunking on all document types: DOCX supports it well; PDFs require document-specific handling. Not adopted as the default for the MVP.
- Semantic chunking as the default: not selected for the current corpus-scale MVP.
- Presidio only, without regex: not selected; the hybrid approach combines Presidio with explicit patterns for common identifiers.

**Operational KPIs** (see `docs/kpi/wk8-snapshot.md`):

- Collection: `capstone_chunks_v2`.
- Documents ingested: 6.
- Chunks stored: 746.
- PII redactions reported during corpus ingestion: 873.
- Retrieval hit rate: 16/18 (88.89%) using top-3 retrieval.
- Week 7 retrieval hit rate: 18/18 (100%).
- Week 8 grounded response rate, query cost and latency: pending measurement.


## W9 — Hybrid retrieval + cross-encoder reranking

**Decision:** The capstone retrieval system was upgraded from W8's pure dense retrieval to hybrid retrieval using BM25 and dense search, followed by cross-encoder reranking.

**Retrieval stack:**
- BM25 library: rank-bm25 (BM25Okapi).
- Tokenization: lowercase text, preserving alphanumeric characters, hyphens, slashes and underscores.
- Dense model: text-embedding-3-small (1536 dimensions).
- Vector store: Qdrant Cloud, collection capstone_chunks_v2.
- Fusion: Reciprocal Rank Fusion (RRF), k=60.
- Reranker: cross-encoder/ms-marco-MiniLM-L-6-v2.
- Hybrid retrieval combines BM25 and dense results into up to 10 candidates.
- Cross-encoder reranking returns the final top 3 results.

**Alternatives considered:**
- Cohere Rerank API: not selected; the implementation uses a local cross-encoder.
- Weighted score fusion: not selected; RRF is used to combine ranked lists.
- Larger cross-encoder: not selected; the current implementation uses MiniLM-L-6-v2.
- LlamaIndex: not introduced; the current retrieval pipeline is implemented using the existing project structure.

**Operational KPIs** (see `docs/kpi/wk9-snapshot.md`):

- W8 Precision@3: 66.7% (12/18).
- W9 Precision@3: 55.6% (10/18).
- Change in Precision@3: -11.1 percentage points.
- W8 Precision@5: 83.3% (15/18).
- W9 Precision@5: 77.8% (14/18).
- Change in Precision@5: -5.6 percentage points.
- W9 cost per query: not measured.
- W9 latency p50: not measured.
- W9 grounded response rate: not measured.

**Known gaps to revisit:**
- W9 did not improve retrieval precision over the W8 dense-only baseline.
- Questions g004 and g018 became top-3 retrieval misses.
- No previously missed in-corpus question became a top-3 hit.
- Abstention behaviour for out-of-corpus questions g019 and g020 has not been evaluated in this W9 run.
- The BM25 index is rebuilt from the Qdrant collection when the retrieval module loads.
- Cross-encoder latency has not been benchmarked for this capstone.

These findings will guide future retrieval evaluation and optimization.

## W10 — Caching + KB lifecycle

**Decisions:**
- **Layer 1 (semantic cache):** SQLite backend (reuse `results.db`); 0.95 cosine similarity threshold; scan-based lookup.
- **Layer 2 (OpenAI prompt cache):** Identified in the W10 guide as implicit caching for supported models. Not separately measured in this capstone evaluation.
- **Layer 3 (embedding cache):** Existing implementation from W7.
- **Tombstone semantics:** `IsEmptyCondition` instead of `IsNullCondition`; used to identify live chunks where `deleted_at` is absent.
- **Update flow:** Tombstone old chunks → insert new chunks → clear semantic cache.
- **Audit escape hatch:** `dense_search(include_deleted=True)` for historical retrieval.

**Rejected alternatives:**
- LLMLingua prompt compression: deferred to optional Stretch; groundedness must be measured before using it.
- Cohere semantic cache API: not used; the capstone uses a local SQLite cache.
- Cache-per-source invalidation: not implemented; the current approach clears the complete cache after an update.
- `IsNullCondition` for tombstone filtering: not used; the implementation uses `IsEmptyCondition`.

**Operational KPIs** (see `docs/kpi/wk10-snapshot.md`):

- Golden set: 20 questions.
- Cold-pass cache hits: 0/20 (0%).
- Warm-pass cache hits: 20/20 (100%).
- Estimated cold-pass cost: $0.00129.
- Estimated warm-pass cost: $0.00001.
- Estimated warm-pass cost saving: 99.5%.
- Cold-pass latency p50: 3,066 ms; p95: 66,245 ms.
- Warm-pass latency p50: 507 ms; p95: 598 ms.
- Precision and grounded response rate: not re-measured in W10.

**Known gaps to revisit:**
- No cache TTL; entries remain until document updates trigger cache clearing.
- Cache invalidation is all-or-nothing rather than source-specific.
- False semantic cache hits need monitoring with varied production questions.
- Cost values are estimates, not actual billing records.
- Token estimation uses whitespace-separated word counts rather than an exact tokenizer.
- The repeated 20-question evaluation does not establish performance on varied real-world traffic.