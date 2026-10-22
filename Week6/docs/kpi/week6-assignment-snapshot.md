# Week 6 Assignment Snapshot — CBSE RAG Chunk-Size Experiment

## 1. Objective

Compare three chunk-size configurations and evaluate how effectively they retrieve relevant source documents from a CBSE curriculum corpus.

## 2. Experimental Setup

- **Corpus:** Six CBSE curriculum and circular PDFs for 2026–27
- **Text extraction:** PyMuPDF
- **Pages with extracted text:** 110
- **Evaluation questions:** 20
- **In-corpus questions:** 18
- **Out-of-corpus questions:** 2
- **Retrieval method:** Embedding-based retrieval
- **Embedding model:** `text-embedding-3-small`
- **Number of retrieved results:** Top 3

## 3. Chunk-Size Configurations

| Profile | Chunk Size | Overlap | Chunks Created |
|---|---:|---:|---:|
| Small | 300 | 30 | 1,038 |
| Medium | 500 | 50 | 640 |
| Large | 800 | 80 | 415 |

## 4. Evaluation Results

| Profile | Source-Match Hits | Questions Scored | Retrieval Hit Rate |
|---|---:|---:|---:|
| Small | 15 | 18 | 83.33% |
| Medium | 16 | 18 | 88.89% |
| Large | 18 | 18 | 100.00% |

The hit rate measures whether at least one expected source document appeared among the top three retrieved results.

## 5. Observations

- The small profile achieved an 83.33% retrieval hit rate.
- The medium profile achieved an 88.89% retrieval hit rate.
- The large profile achieved a 100% retrieval hit rate on the 18 in-corpus questions.
- The large profile produced fewer chunks than the small and medium profiles.
- Cost per query was not measured.

## 6. Limitations

- The evaluation contains only 18 scored in-corpus questions.
- Retrieval hit rate does not establish whether the generated answers are correct.
- The two out-of-corpus questions still require separate abstention testing.
- Four PDF pages had limited text extraction, and some extracted Hindi text was distorted.
- API cost and latency were not measured.

## 7. Conclusion and Recommendation

Based on source-match retrieval hit rate, the large configuration (800-character chunks with 80-character overlap) performed best on this CBSE evaluation set.

Before choosing it as the final configuration, evaluate answer quality, test abstention on out-of-corpus questions, and measure cost and latency.

These findings apply to the current corpus and evaluation set; they do not establish that larger chunks will always perform better.