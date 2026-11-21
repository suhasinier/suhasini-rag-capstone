# W8 — Document ingestion and PII protection

## Decision

The capstone will use a dedicated ingestion pipeline to process source documents before storing them in the Qdrant Cloud collection `capstone_chunks_v2`.

The pipeline will parse documents, split their content into chunks, scrub personally identifiable information (PII), enrich each chunk with metadata, generate embeddings and upsert the results into Qdrant.

## Ingestion pipeline

The processing sequence is:

1. Parse documents according to their file extensions.
2. Split the extracted content using recursive chunking (maximum chunk size: 400).
3. Apply hybrid PII scrubbing using regular expressions and Presidio.
4. Enrich chunks with metadata (9 fields).
5. Generate embeddings using `text-embedding-3-small`.
6. Upsert the chunks and embeddings into `capstone_chunks_v2`.

## PII protection

The ingestion pipeline uses a combination of regular expressions and Presidio.

- Regex patterns detect EMAIL, PHONE and EMP_ID.
- Presidio detects PERSON, LOCATION and ORGANIZATION.
- PII is scrubbed during ingestion, before the chunks are stored in the vector database.

The Week 8 corpus ingestion reported 873 redactions.

The separate stress-test findings document records additional limitations, including missed obfuscated emails, partially redacted international phone numbers and custom employee ID formats.

These findings indicate that hybrid detection does not guarantee complete PII removal.

## Vector stack

- Embedding model: text-embedding-3-small
- Embedding dimensions: 1536
- Vector store: Qdrant Cloud
- Collection: capstone_chunks_v2
- Distance metric: cosine
- Total points ingested: 746

## Operational changes

- A dedicated document ingestion pipeline is introduced.
- PII scrubbing is performed before data is stored.
- Metadata is expanded to 9 fields.
- Metadata enables filtered retrieval.
- The Week 7 collection `capstone_chunks` is retained as the earlier baseline.
- Week 8 evaluation and KPI measurements are recorded in `docs/kpi/wk8-snapshot.md`.

## Validation

- Successfully ingested 6 PDF documents.
- Generated 746 chunks.
- Generated embeddings for all 746 chunks.
- Upserted 746 points into `capstone_chunks_v2`.
- Confirmed that the Qdrant collection contains 746 points with 1536-dimensional vectors.
- Recorded 873 PII redactions during corpus ingestion.
- Evaluated retrieval using the same 20-question golden set.
- Week 8 retrieval hit rate: 16/18 in-corpus questions (88.89%) using top-3 retrieval.
- Two expected source documents were not retrieved in the top 3, although relevant content was present in the collection.

## Known limitations

- PII stress testing identified formats that were missed or only partially redacted.
- Proposed improvements to employee ID detection, email normalisation and phone-number detection have not yet been integrated into the main `scrub_chunks()` function.
- Grounded response rate, query cost and latency have not yet been measured for Week 8.
- The retrieval hit rate is lower than the Week 7 baseline; the exact cause has not yet been established.

## Data residency

- Embeddings and LLM inference use the OpenAI API (US).
- Qdrant Cloud region: `eu-central-1`.
- Application-layer region: not confirmed.

