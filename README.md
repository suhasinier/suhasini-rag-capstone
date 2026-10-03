# AI-Powered Education & Curriculum Assistant

A capstone project for building an AI-powered assistant that helps users understand and work with CBSE and NCERT curriculum, assessment, and education-framework documents.

The project is being developed as part of an **Agentic AI & RAG Engineering** learning journey, progressing from basic LLM interaction to production-oriented RAG and AI application engineering.

---

## Project Goal

The goal of this capstone is to build an AI-powered education assistant that provides answers grounded in a selected collection of education documents rather than relying only on the language model's general knowledge.

The project uses concepts such as:

* Large Language Model (LLM) interaction
* Retrieval-Augmented Generation (RAG)
* Structured LLM outputs
* Asynchronous API calls
* Retry and backoff handling
* Logging and persistence
* API development
* Testing
* Cost tracking
* Application-level validation

---

## Corpus

The intended corpus consists of publicly available CBSE and NCERT curriculum, assessment, and education-framework documents.

**Sources:** Official CBSE and NCERT websites.

The corpus provides the knowledge base that the eventual RAG application can use to produce grounded responses.

---

# Phase 1

Phase 1 covers the initial engineering journey from understanding the problem and working with an LLM to building the foundations of a production-oriented AI/RAG application.

It includes:

* Week 1 — LLM foundations and system prompts
* Week 2 — Async Python, structured outputs, retries, logging and persistence
* Week 3 — API application and testing
* Week 4 — Cost tracking and richer structured responses
* Week 5 — Graded Mini Project

---

# Week 1 — LLM Foundations

Week 1 introduced the basic building blocks for working with an LLM.

### Main concepts

* Problem and solution framing
* RAG vs. fine-tuning vs. long-context approaches
* Agent frameworks and tool-based systems
* Basic LLM/API interaction
* System prompts
* Prompt-driven behaviour
* Experiment evidence

### Hands-on work

The Week 1 work included building and running a basic LLM interaction program:

```text
Week1/src/hello_llm.py
```

The program established the basic pattern of:

```text
Application
    ↓
OpenAI client
    ↓
LLM request
    ↓
Response
```

Week 1 also explored how changing a **system prompt** can change the tone, style, vocabulary, and behaviour of the same underlying LLM.

The Week 1 project materials include:

```text
Week1/
├── README.md
├── docs/
│   ├── adr/
│   └── runs/
├── guides/
├── requirements.txt
└── src/
    └── hello_llm.py
```

The architecture decision record and experiment/run documentation are retained as part of the project history.

---

# Week 2 — Production-Oriented Python Foundations

Week 2 moved from a simple LLM call to a more structured asynchronous pipeline.

The focus was on learning the engineering foundations required for building reliable AI applications.

### Main concepts

* Pydantic models
* Typed data
* JSON validation
* Asynchronous Python
* `asyncio`
* `asyncio.gather`
* `httpx.AsyncClient`
* Batch processing
* Retry handling
* Exponential backoff
* JSON logging
* Environment variables and secrets
* SQLite persistence
* AI coding-assistant workflow

### Structured outputs

Pydantic was used to make sure that data returned by the LLM/application matched an expected structure.

For example, models were used for runtime configuration and run summaries.

### Async pipeline

Instead of making API calls one after another:

```text
Call 1 → wait
Call 2 → wait
Call 3 → wait
...
```

the Week 2 pipeline introduced asynchronous execution:

```text
          ┌── Call 1
          ├── Call 2
Question ─┼── Call 3
          ├── Call 4
          └── ...
                ↓
          Collect results
```

`asyncio.gather()` was used to run multiple independent operations concurrently.

### Reliability

The pipeline introduced retry handling with exponential backoff:

```text
Attempt
   ↓
failure?
   ↓
wait 1s
   ↓
retry
   ↓
wait 2s
   ↓
retry
   ↓
wait 4s
```

### Persistence

SQLite was introduced as a lightweight persistence mechanism.

The Week 2 database contains runtime information including:

* runs
* answers

The Week 2 output also includes JSON results and pipeline logs.

### Week 2 structure

```text
Week2/
├── data/
│   └── questions.csv
├── docs/
│   └── lab2-assistant-notes.md
├── guides/
│   ├── AI-RAG_W2_Lab_Guide_2Day.md
│   ├── AI-RAG_W2_Practice_Assignment.md
│   ├── W2_Activity_Solution.md
│   └── sample_week2-activity.md
├── logs/
│   └── pipeline.log
├── requirements.txt
├── results.db
├── results.json
└── src/
    └── pipeline/
        ├── __init__.py
        ├── fake_llm.py
        ├── logging_config.py
        ├── pipeline.py
        ├── query_results.py
        ├── settings.py
        └── store.py
```

---

# Week 3 — Application API and Testing

Week 3 extended the pipeline into an application/API layer.

The work introduced the idea of exposing the AI pipeline through a web API rather than treating it only as a Python script.

### Main concepts

* FastAPI
* Uvicorn
* API endpoints
* Request/response models
* OpenAPI documentation
* API testing
* Pytest
* Async testing
* Fake LLM testing
* Separating application code from pipeline logic

The Week 3 work included an API application and testing around the pipeline.

The API was run using Uvicorn and tested through HTTP requests.

The Week 3 work also introduced the importance of testing individual pieces of the pipeline rather than relying only on manual execution.

The project used a fake LLM during testing so that pipeline behaviour could be tested without making unnecessary real API calls.

---

# Week 4 — Cost Tracking and Structured Responses

Week 4 built on the Week 3 pipeline and introduced additional production-oriented concerns.

### Main concepts

* LLM token usage
* `tiktoken`
* Cost calculation
* Model-specific pricing
* Pydantic response models
* Backward-compatible model evolution
* Confidence information
* Sources
* Schema versioning
* API integration

A cost calculation component was introduced to estimate the USD cost of LLM calls.

The Week 4 model structure retained the earlier response fields while adding new optional information such as:

```text
confidence
sources
schema_version
```

This demonstrated how an API contract can evolve while preserving compatibility with earlier clients.

Week 4 also continued the API/application work and included checks for the expected project structure and behaviour.

---

# Week 5 — Graded Mini Project

The next major Phase 1 component is the graded Mini Project.

The mini project brings together the engineering concepts developed during the earlier weeks and applies them to a more complete AI/RAG application.

The repository contains the mini-project work under:

```text
mp1/
```

The mini project is treated separately from the weekly learning materials so that the completed weekly engineering work remains clearly organized.

---

# Repository Structure

The repository is organized by learning phase/week rather than keeping all Python files in one common `src/` directory.

```text
suhasini-rag-capstone/
│
├── .gitignore
├── README.md
│
├── Week1/
│   ├── README.md
│   ├── docs/
│   ├── guides/
│   ├── requirements.txt
│   └── src/
│
├── Week2/
│   ├── data/
│   ├── docs/
│   ├── guides/
│   ├── logs/
│   ├── requirements.txt
│   ├── results.db
│   ├── results.json
│   └── src/
│
├── Week3/
│   └── ...
│
├── W4_package/
│   └── ...
│
└── mp1/
    └── ...
```

The repository structure is intentionally being organized so that each week's learning materials, code, experiments, and supporting files can be understood independently.

---

# Engineering Journey

The progression through Phase 1 can be viewed as:

```text
Week 1
Basic LLM interaction
        ↓
System prompts and experimentation
        ↓
Week 2
Typed data + Async Python
        ↓
Batching + Retry + Logging
        ↓
SQLite persistence
        ↓
Week 3
Application/API layer
        ↓
FastAPI + Uvicorn
        ↓
Testing
        ↓
Week 4
Cost awareness
        ↓
Structured API responses
        ↓
Schema evolution
        ↓
Week 5
Mini Project
        ↓
Integrated application work
```

The overall direction is from **understanding how an LLM works in a simple application** toward **engineering reliable, testable and maintainable AI/RAG applications**.

---

# Current Phase

**Phase 1 — Completed**

Phase 1 currently includes:

* Week 1
* Week 2
* Week 3
* Week 4
* Week 5 Mini Project

This README will be updated as the capstone progresses through subsequent phases and additional project work.
