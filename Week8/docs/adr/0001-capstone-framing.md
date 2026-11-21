
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

