# ADR-0001: Capstone Framing — AI-Powered Education & Curriculum Assistant

- **Status:** Draft v1
- **Date:** 2026-08-20
- **Author:** Suhasini Ramachandran

## Context

This capstone aims to build an AI-powered assistant that helps educators and learners understand and work with CBSE and NCERT curriculum, assessment, and education-framework documents. The goal is to provide reliable, document-grounded answers instead of depending only on the general knowledge of an LLM.

## Decision — Solution Framing Canvas

| Box | Our answer |
|-----|------------|
| **Inputs** | A user provides a natural-language question about CBSE/NCERT curriculum, learning outcomes, assessment, or education frameworks. |
| **Outputs** | The system produces a concise, grounded answer based on the relevant education documents, with source references where possible. |
| **Tools** | The system will use an OpenAI language model and, in later weeks, a retrieval component over the selected CBSE/NCERT document corpus. |
| **Memory** | Version 1 will not retain information between separate user sessions; each question will be treated independently. |
| **Autonomy level** | The system will initially operate as a RAG-based Q&A assistant: it retrieves relevant information and generates an answer but does not independently take actions. |
| **Decision boundaries** | The system may answer questions supported by the retrieved documents; when sufficient evidence is unavailable or the question requires professional human judgment, it should clearly indicate uncertainty rather than invent an answer. |

## Consequences

- **Positive:** The assistant can provide faster access to information across multiple education documents; grounding answers in source documents can reduce unsupported answers; the project demonstrates practical RAG engineering in an education domain.
- **Negative / risks:** The quality of answers depends on the quality and currency of the selected documents; incorrect retrieval can lead to incorrect answers; the system may still hallucinate when the available evidence is insufficient.
- **Things we'll re-visit:** Retrieval and confidence/evaluation strategies will be revisited in later weeks; memory and more agentic behaviour may be considered later if the core Q&A system proves reliable.
