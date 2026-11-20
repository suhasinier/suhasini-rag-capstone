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


---

## Local embedding experiment — MiniLM

### Objective

Evaluate whether a free, locally running embedding model can replace hosted OpenAI embeddings for the CBSE Class 9 capstone retrieval system.

### Configuration

| Property | Value |
|---|---|
| Local embedding model | all-MiniLM-L6-v2 |
| Execution | Local |
| Vector dimensions | 384 |
| Corpus chunks | 415 |
| Qdrant collection | capstone_chunks_local |
| Vector distance | Cosine |
| Batch size during migration | 32 |
| Evaluation dataset | Week6/data/golden_set_cbse_class9_wk6_14-4-2.jsonl |
| Top-k retrieval | 3 |

### Retrieval accuracy comparison

| Metric | OpenAI hosted (text-embedding-3-small) | MiniLM local |
|---|---:|---:|
| Embedding dimensions | 1536 | 384 |
| Corpus chunks | 415 | 415 |
| In-corpus questions | 18 | 18 |
| Retrieval hits | 18 | 14 |
| Retrieval misses | 0 | 4 |
| Retrieval hit rate | 100.00% | 77.78% |
| Out-of-corpus questions | 2 | 2 |

The same golden set and source-match evaluation criteria were used for both models. A hit means at least one expected source appeared among the top three retrieved results.

### Local retrieval latency

- Median retrieval latency (p50): 162.73 ms.
- First query latency: 37,844.73 ms, including initial model-loading overhead.
- Subsequent query latencies were approximately 159–188 ms.
- Timing includes local query embedding and Qdrant search.
- This is a single evaluation run; latency may vary.

The existing hosted benchmark measures end-to-end RAG latency, whereas this local measurement covers query embedding and retrieval. These latency figures are not directly comparable.

### Cost and operational considerations

| Property | OpenAI hosted embeddings | MiniLM local |
|---|---|---|
| Embedding API | Required | Not required |
| Per-request embedding API charge | Yes | No |
| Model execution | Hosted service | Local computation |
| Vector dimensions | 1536 | 384 |
| Model download | Not required locally | Required initially |
| External embedding dependency | Yes | No, after model download |
| Local compute requirement | No local embedding model | Yes |

Local embeddings avoid per-request embedding API charges. However, local computation, storage, and infrastructure still have costs.

### Retrieval misses with MiniLM

The local model missed four in-corpus questions:

- g003
- g007
- g014
- g016

The other 14 in-corpus questions retrieved at least one expected source in the top three results.

#### Investigation: g003

- Question: When may a foreign language be offered in the revised language scheme?
- Expected source: `33_Circular_2026.pdf`
- Retrieved source: `Curriculum_SecP1_2026-27.pdf`
- Top-3 similarity scores: 0.5583, 0.5393, 0.5380.
- The third-ranked chunk discusses school autonomy and conditions for offering a foreign language along with two native Indian languages or as a fourth additional language.
- The retrieved content is semantically relevant, but it does not come from the expected source.
- This illustrates the difference between semantic relevance and expected-source matching.

#### Investigation: g007

- Question: How are marks divided between the Class IX English written examination and internal assessment?
- Expected source: `English_LL_SecP1IX_2026-27.pdf`
- Retrieved source: `Curriculum_SecP1_2026-27.pdf`
- Top-3 similarity scores: 0.7317, 0.7005, 0.6527.
- The second-ranked chunk contains the general Class IX assessment structure of 80 marks for the annual examination and 20 marks for internal assessment.
- The retrieved content is relevant to assessment marks, but the expected English syllabus was not retrieved.
- This is a source-match failure. The English-specific marks distribution should be verified against the original English syllabus before judging answer correctness.

#### Investigation: g014

- Question: How does the Class IX Science syllabus divide assessment between theory and internal assessment?
- Expected source: `ScienceSt_SecP1_2026-27.pdf`
- Retrieved source: `Curriculum_SecP1_2026-27.pdf`
- Top-3 similarity scores: 0.7024, 0.6575, 0.6559.
- The first chunk discusses the general Class IX internal assessment framework.
- The second and third chunks contain general subject assessment structures mentioning Science, but do not provide the exact Science-specific theory and internal assessment marks distribution.
- MiniLM retrieved broadly related assessment information but did not retrieve the expected Science syllabus.
- This is a source-match failure. The exact Science marks distribution should be verified against the original Science syllabus before judging answer correctness.

#### Investigation: g016

- Question: A Class IX Science teacher wants to design a lesson and assessment plan. How should the teacher use both the syllabus content and the assessment information in the Science curriculum?
- Expected source: `ScienceSt_SecP1_2026-27.pdf`
- Retrieved source: `Curriculum_SecP1_2026-27.pdf`
- Top-3 similarity scores: 0.5946, 0.5813, 0.5700.
- The first chunk discusses competency-based teaching, formative assessment and teaching-learning processes.
- The second chunk mentions the Mathematics and Science syllabus and assessment requirements.
- The third chunk discusses integrated teaching approaches and competency-focused assessment.
- The retrieved information is broadly relevant to lesson planning and assessment, but the expected Science syllabus was not retrieved.
- This is a source-match failure. Subject-specific syllabus and assessment details should be verified against the original Science syllabus.

### Results files

- Hosted evaluation: `Week7/data/eval/qdrant.json`
- Local evaluation: `Week7/data/eval/qdrant_local.json`
- Local migration script: `Week7/scripts/migrate_local_to_qdrant.py`
- Local embedding implementation: `Week7/src/rag/embeddings_local.py`
- Local retrieval implementation: `Week7/src/rag/qdrant_local_rag.py`
- Local evaluation script: `Week7/scripts/run_qdrant_local_eval.py`

### Preliminary conclusion

For this 415-chunk CBSE Class 9 corpus and the 18 scored questions, OpenAI text-embedding-3-small achieved a higher retrieval hit rate (100.00%) than MiniLM (77.78%).

MiniLM offers an alternative that avoids per-request embedding API charges and produces smaller 384-dimensional vectors. However, its four retrieval misses indicate a reduction in retrieval quality for this particular evaluation.

The current evidence therefore favours text-embedding-3-small when retrieval accuracy is the priority. MiniLM remains a useful option when avoiding hosted embedding API dependencies and reducing vector dimensionality are important.

This is a preliminary comparison based on one evaluation run. Further testing, including out-of-corpus abstention behaviour and repeated latency measurements, is needed before making a final production choice.

---

## Final Reflection and Verdict

### 1. Cost

- MiniLM generates embeddings locally without per-request embedding API charges.
- The model requires an initial download and local computing resources.
- OpenAI hosted embeddings involve API usage charges.
- Local embeddings may be economical for repeated embedding operations, depending on available computing resources and usage volume.

### 2. Privacy

- MiniLM can generate embeddings locally without sending document text or user queries to an external embedding API.
- After downloading the model, embedding generation can work without contacting the model provider.
- The Qdrant collection in this experiment is hosted on Qdrant Cloud, so local embedding generation does not mean the entire retrieval system is private or offline.

### 3. Quality

- OpenAI text-embedding-3-small achieved 100% retrieval hit rate (18/18).
- MiniLM achieved 77.78% retrieval hit rate (14/18).
- MiniLM missed four questions: g003, g007, g014 and g016.
- Investigation showed that these misses retrieved broadly related content from the general curriculum document instead of the expected subject-specific documents.

### 4. Final Verdict

For the current CBSE Class 9 capstone corpus, OpenAI text-embedding-3-small is preferred when retrieval accuracy is the primary requirement.

MiniLM is a useful alternative when reducing embedding API dependency, vector dimensions and recurring embedding API charges is more important.

The experiment demonstrates that a free local embedding model can be integrated with the existing RAG architecture and Qdrant vector database. However, the observed retrieval accuracy difference means that it should not be treated as a direct quality-equivalent replacement for the hosted model.

This conclusion is based on one evaluation run using 18 scored questions. Further testing would be required before making a production deployment decision.