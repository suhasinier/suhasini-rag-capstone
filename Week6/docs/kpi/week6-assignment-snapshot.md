# Week 6 Assignment Snapshot — CBSE RAG Chunk-Size and Embedding Experiment

## 1. Objective

Compare three chunk-size configurations and evaluate how effectively they retrieve relevant source documents from a CBSE curriculum corpus. Additionally, compare OpenAI embeddings with locally generated embeddings using Sentence Transformers.

## 2. Experimental Setup

- **Corpus:** Six CBSE curriculum and circular PDFs for 2026–27
- **Text extraction:** PyMuPDF
- **Pages with extracted text:** 110
- **Evaluation questions:** 20
- **In-corpus questions:** 18
- **Out-of-corpus questions:** 2
- **Retrieval method:** Embedding-based retrieval
- **Number of retrieved results:** Top 3

## 3. Activity A — Chunk-Size Experiment

### Chunk-Size Configurations

| Profile | Chunk Size | Overlap | Chunks Created |
|---|---:|---:|---:|
| Small | 300 | 30 | 1,038 |
| Medium | 500 | 50 | 640 |
| Large | 800 | 80 | 415 |

### Evaluation Results

| Profile | Source-Match Hits | Questions Scored | Retrieval Hit Rate |
|---|---:|---:|---:|
| Small | 15 | 18 | 83.33% |
| Medium | 16 | 18 | 88.89% |
| Large | 18 | 18 | 100.00% |

The hit rate measures whether at least one expected source document appeared among the top three retrieved results.

### Observations

- The small profile achieved an 83.33% retrieval hit rate.
- The medium profile achieved an 88.89% retrieval hit rate.
- The large profile achieved a 100% retrieval hit rate on the 18 in-corpus questions.
- The large profile produced fewer chunks than the small and medium profiles.
- Cost per query was not measured.

## 4. Activity B — Local Embeddings with Sentence Transformers

### Objective

Replace the OpenAI embedding model, `text-embedding-3-small`, with a locally running Sentence Transformers model, `all-MiniLM-L6-v2`, and compare retrieval performance.

### Embedding Models

| Feature | OpenAI Baseline | Local Embeddings |
|---|---|---|
| Model | text-embedding-3-small | all-MiniLM-L6-v2 |
| Provider | OpenAI API | Sentence Transformers |
| Vector dimensions | 1,536 | 384 |
| Embedding generation | API-based | Local machine |
| API cost for embedding queries | Not separately measured | No per-query API charge after setup |

### Local Index Setup

- **Source documents:** 110 extracted CBSE page documents
- **Chunk size:** 500
- **Overlap:** 50
- **Chunks created:** 640
- **Embedding model:** all-MiniLM-L6-v2
- **Vector dimensions:** 384
- **Index file:** `data/embeddings_local.json`

The same 500-character chunk size and 50-character overlap used in the Activity A medium profile were retained for this comparison.

### Retrieval Evaluation Results

| Metric | OpenAI Medium Baseline | Local Embeddings |
|---|---:|---:|
| Retrieval hits | 16 | 12 |
| Questions scored | 18 | 18 |
| Retrieval hit rate | 88.89% | 66.67% |

The two out-of-corpus questions were excluded from both hit-rate calculations.

### Five-Question Source Comparison


| Question ID | OpenAI Top Source | Local Top Source | Same Source? | OpenAI Cosine | Local Cosine |
|---|---|---|---|---:|---:|
| g001 | Curriculum_SecP1_2026-27.pdf | Curriculum_SecP1_2026-27.pdf | Yes | 0.5196 | 0.6008 |
| g002 | Curriculum_SecP1_2026-27.pdf | Curriculum_SecP1_2026-27.pdf | Yes | 0.6929 | 0.6787 |
| g003 | Curriculum_SecP1_2026-27.pdf | Curriculum_SecP1_2026-27.pdf | Yes | 0.6416 | 0.6100 |
| g004 | Curriculum_SecP1_2026-27.pdf | Curriculum_SecP1_2026-27.pdf | Yes | 0.6727 | 0.7113 |
| g005 | 33_Circular_2026.pdf | Curriculum_SecP1_2026-27.pdf | No | 0.4694 | 0.5325 |


**Top-source agreement:** 4 out of 5 questions (80%).

The two models' cosine similarity scores were also recorded. However, their absolute values should not be compared directly because the models generate vectors in different embedding spaces.

### Observations

- Local embeddings achieved a 66.67% retrieval hit rate.
- The OpenAI medium baseline achieved 88.89%.
- Local retrieval produced four fewer source-match hits than the OpenAI baseline.
- The top retrieved source matched between the two models for four of the five manually compared questions.
- Local embeddings use a smaller 384-dimensional vector representation compared with the OpenAI model's 1,536 dimensions.
- Local embedding generation does not incur a per-query API charge after setup.
- The initial model download and setup require time and local computing resources.
- Exact API cost per query and latency p50 were not measured.

## 5. Overall Observations

- In Activity A, the large chunk configuration (800/80) achieved the highest retrieval hit rate of 100%.
- In Activity B, the local embedding model achieved 66.67%, compared with 88.89% for the OpenAI medium baseline.
- The five-question comparison showed 80% agreement in the top retrieved source.
- Chunk size and embedding model both influence retrieval performance.
- A model with lower operating cost may involve a trade-off in retrieval quality.
- Retrieval hit rate alone does not establish whether the final generated answer is correct.

## 6. Limitations

- The evaluation contains only 18 scored in-corpus questions.
- Retrieval hit rate does not establish whether generated answers are correct.
- The two out-of-corpus questions still require separate abstention testing.
- Four PDF pages had limited text extraction, and some extracted Hindi text was distorted.
- API cost and latency were not measured.
- The five-question source comparison is a small sample and should not be treated as a complete comparison of both models.
- Local embedding performance was evaluated using the current CBSE corpus and golden question set only.

## 7. Conclusion and Recommendation

Based on source-match retrieval hit rate, the large chunk configuration (800-character chunks with 80-character overlap) performed best in Activity A.

For Activity B, OpenAI `text-embedding-3-small` performed better than the local `all-MiniLM-L6-v2` model on the current evaluation set. The local model achieved 66.67% compared with the OpenAI medium baseline's 88.89%.

Local embeddings offer the advantage of avoiding per-query embedding API charges after setup. However, the observed reduction in retrieval performance should be considered before choosing them for deployment.

For the current CBSE RAG project, the OpenAI medium configuration is the stronger choice based on the measured retrieval results. Local embeddings could still be considered where avoiding API dependency and recurring embedding costs is a priority, provided retrieval quality is improved and validated.

Before final deployment, evaluate answer quality, test abstention on out-of-corpus questions, and measure actual cost and latency.

These findings apply to the current corpus and evaluation set; they do not establish that larger chunks or a particular embedding model will always perform better.

### Recommendation for a 10× Larger Corpus

If the corpus were 10 times larger, I would initially consider local embeddings because they avoid recurring API charges for embedding generation and reduce dependence on an external embedding service. However, my current experiment shows that the local model achieved a lower retrieval hit rate (66.67%) than the OpenAI baseline (88.89%). Therefore, I would not switch to local embeddings without further testing and quality improvements. For the current project, I would retain the OpenAI medium configuration until the local model demonstrates acceptable retrieval quality, cost savings, and performance at the larger scale.