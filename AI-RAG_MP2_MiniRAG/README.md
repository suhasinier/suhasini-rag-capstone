# MP2 · Mini-RAG — Ask Your Documents

**Mini Project 2 · Week 9 deliverable · Phase 2 (Retrieval / RAG)**

A standalone end-to-end Retrieval-Augmented Generation (RAG) project. This project demonstrates the complete RAG workflow using a small Sherlock Holmes corpus.

## Project Overview

Build a question-answering system that retrieves relevant passages from a document collection and uses an LLM to generate answers with source citations.

**Core workflow:**

Load documents → Chunk documents → Generate embeddings → Store in Qdrant → Retrieve relevant chunks → Generate answers.

**Technology stack:**
- Python 3.11
- OpenAI `gpt-4o-mini`
- OpenAI `text-embedding-3-small`
- Qdrant Cloud
- BM25 keyword retrieval (optional stretch)
- Reciprocal Rank Fusion (RRF) (optional stretch)
- Cross-encoder reranking (optional stretch)

## Project Structure

```text
AI-RAG_MP2_MiniRAG/
│
├── README.md
└── learner/
    ├── mp2_rag.py
    ├── mp2_reflection.md
    ├── mp2_validation.txt
    ├── requirements.txt
    ├── .env.example
    ├── corpus/
    │   ├── 01_red_headed_league.txt
    │   ├── 02_speckled_band.txt
    │   ├── 03_blue_carbuncle.txt
    │   ├── 04_engineers_thumb.txt
    │   └── 05_scandal_in_bohemia.txt
    └── data/
        ├── predefined_questions.jsonl
        └── learner_questions.jsonl
```

## Environment Setup (Windows PowerShell)

Open the terminal inside the `learner` folder.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create the `.env` file using `.env.example` as the template and configure the required API and Qdrant credentials.

**Important:** Never include `.env`, API keys, Qdrant credentials, or the `.venv` folder in the submission ZIP.

## Running the Project

Run the following commands from the `learner` folder:

```powershell
python mp2_rag.py ingest
python mp2_rag.py validate
python mp2_rag.py ask
```

- `ingest` loads the corpus, creates chunks, generates embeddings and stores them in Qdrant.
- `validate` tests the predefined and learner-authored questions.
- `ask` allows interactive question answering.

Ingestion is a one-time setup for the project collection. Do not recreate or ingest into an existing collection unnecessarily.

## Corpus

The project uses five Sherlock Holmes story summaries:

- `01_red_headed_league.txt` — The Red-Headed League
- `02_speckled_band.txt` — The Adventure of the Speckled Band
- `03_blue_carbuncle.txt` — The Adventure of the Blue Carbuncle
- `04_engineers_thumb.txt` — The Adventure of the Engineer's Thumb
- `05_scandal_in_bohemia.txt` — A Scandal in Bohemia

The summaries are based on Arthur Conan Doyle's public-domain stories.

## Implementation Summary

The core implementation includes:

1. Loading the five text documents.
2. Splitting documents into overlapping chunks.
3. Generating 1536-dimensional embeddings.
4. Creating a Qdrant collection using cosine similarity.
5. Storing 75 document chunks in Qdrant.
6. Retrieving relevant chunks using dense vector search.
7. Generating answers using the retrieved context and providing source citations.

The Qdrant retrieval implementation uses `query_points()` for compatibility with the installed Qdrant client.

## Optional Stretch: Hybrid Search and Reranking

The optional stretch implementation adds:

- BM25 keyword-based retrieval.
- Reciprocal Rank Fusion (RRF) to combine dense and keyword retrieval.
- Cross-encoder reranking using `cross-encoder/ms-marco-MiniLM-L-6-v2`.

The dense and hybrid approaches were compared using all five project questions.

For this Sherlock Holmes narrative corpus, dense retrieval performed better overall in the comparison. Both approaches achieved 5/5 expected source matches, while dense retrieval matched more expected answer phrases and had lower average latency.

The comparison and observations are documented in `mp2_reflection.md`.

## Submission Contents

The final submission includes:

- `mp2_rag.py` — completed RAG implementation.
- `data/learner_questions.jsonl` — three learner-authored questions.
- `mp2_reflection.md` — project reflection and optional stretch comparison.
- `mp2_validation.txt` — validation results.
- `requirements.txt` — project dependencies.
- `corpus/` — five source documents.
- `data/predefined_questions.jsonl` — predefined validation questions.
- `README.md` — project instructions and overview.

**Do not submit:** `.env`, `.venv`, API keys, Qdrant credentials, or downloaded model-cache files.