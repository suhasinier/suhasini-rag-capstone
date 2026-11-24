# MP2 Reflection – Mini-RAG: Ask Your Documents

## What worked

1. **Corpus loading**

   Successfully loaded all five Sherlock Holmes story documents from the corpus folder. The `load_corpus()` function reads each text file, extracts its title, and stores the source filename, title, and full text in a structured dictionary.

2. **Text chunking**

   Implemented fixed-window chunking with a target chunk size of 500 characters and an overlap of 80 characters. This produced 75 chunks from the five documents.

   The overlap helps preserve some context between consecutive chunks, reducing the possibility of losing information when a relevant passage falls near a chunk boundary.

3. **Embedding generation**

   Used the `text-embedding-3-small` model to convert text chunks into numerical vectors. Verified that each embedding contains 1536 dimensions and that multiple input texts produce corresponding embedding vectors.

4. **Vector database setup**

   Successfully created the Qdrant collection named `mp2_sherlock`, configured for 1536-dimensional vectors and cosine similarity.

5. **Document ingestion**

   Generated embeddings for all 75 chunks and stored them in Qdrant along with their metadata, including the source filename, story title, section, and text.

   Verified that all 75 points were successfully stored in the collection.

6. **Semantic retrieval**

   Implemented the `retrieve()` function to convert a user's question into an embedding and retrieve the top three matching chunks from Qdrant.

   The retrieved results include the original chunk information and similarity scores, allowing the application to identify which passages are most relevant to a question.

7. **Answer generation**

   Implemented the `answer()` function to combine the retrieved passages with the user's question and send them to `gpt-4o-mini`.

   The generated response includes the answer, citation details identifying the retrieved source passages, and the total processing latency.

8. **Validation**

   Successfully validated all five questions: two predefined questions and three questions created independently.

   All five questions cited their expected source documents, giving a source-match result of 5/5.

## What didn't work

1. **Qdrant API compatibility**

   The initial retrieval implementation used `qdrant.search()`, but the installed Qdrant client version (1.20.0) did not provide that method. I changed the implementation to use `qdrant.query_points()`, which successfully retrieved the required results.

2. **Expected-fact matching**

   Although all five questions retrieved the expected source documents, the predefined questions had relatively low expected-fact matches: 2/5 and 2/6.

   This showed that retrieving the correct document does not necessarily mean that the generated answer will contain every expected detail.

3. **Retrieval of semantically similar passages**

   During testing, some retrieved chunks came from a different Sherlock Holmes story, even when the question concerned a particular story. This indicated that passages with similar language or context can receive relatively high semantic similarity scores.

## What I'd change

1. Experiment with paragraph-aware chunking so that related sentences and events are more likely to remain together.

2. Evaluate different chunk sizes and overlap values to understand how they affect retrieval relevance and answer quality.

3. Explore ways to improve retrieval when different stories contain similar names, events, or descriptions.

4. Improve answer evaluation beyond simple expected-phrase matching so that factual correctness can be assessed more meaningfully.

## One surprise

One important learning was that a RAG application involves more than simply retrieving the correct document.

Even when the expected source document is retrieved, the final answer depends on which specific chunks are selected and how the language model uses the retrieved context.

I was also surprised that semantic search could retrieve relevant passages even when the user's question was phrased differently from the original story.

This project helped me understand how document loading, chunking, embeddings, vector storage, semantic retrieval, and LLM-based answer generation work together in an end-to-end RAG pipeline.

### Optional Stretch: Hybrid Search and Cross-Encoder Reranking

I implemented BM25 keyword retrieval, Reciprocal Rank Fusion (RRF), and cross-encoder reranking using `cross-encoder/ms-marco-MiniLM-L-6-v2`.

I compared the original dense retrieval pipeline with the hybrid + reranking pipeline using all five project questions.

**Comparison results:**

| Evaluation | Dense only | Hybrid + reranking |
|---|---:|---:|
| Correct source matches | 5/5 | 5/5 |
| Expected facts matched | 11/19 | 8/19 |
| Average latency | 4.08 seconds | 6.48 seconds |

Both methods successfully retrieved passages from the expected source documents for all five questions.

However, dense retrieval matched more of the expected answer phrases and had lower average latency. The difference was particularly noticeable in the questions about John Clay and the planned bank robbery.

For the Blue Carbuncle and Irene Adler questions, both methods produced equivalent answers. For the Speckled Band question, both identified the murder weapon but provided different explanatory details.

**What I learned:**

Hybrid retrieval does not automatically improve RAG performance. BM25, dense retrieval and cross-encoder reranking each contribute a different retrieval perspective, but the final answer still depends on the quality and completeness of the selected passages.

For this narrative Sherlock Holmes corpus and these five evaluation questions, dense retrieval performed better overall. Hybrid retrieval may be more beneficial for collections containing rare exact-match terms, identifiers or technical vocabulary.

I therefore retained dense retrieval as the primary implementation and kept hybrid retrieval with cross-encoder reranking as an optional extension.