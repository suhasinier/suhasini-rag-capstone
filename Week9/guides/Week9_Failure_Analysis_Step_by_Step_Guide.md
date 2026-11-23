# Week 9 – Failure Analysis Step-by-Step Guide

## 1. Purpose

The purpose of this activity is to understand why retrieval still fails even after implementing hybrid search (BM25 + dense retrieval), RRF fusion and cross-encoder reranking.

Instead of adding another retrieval technique immediately, we inspect the retrieved chunks, generated answers and original corpus to identify the actual cause of failure.

**Final deliverable:** `docs/wk9-failure-analysis.md`

## 2. Identify five failed questions

Open:

`docs/wk9-precision-delta.md`

Identify five questions for which `hybrid_rerank` has Precision@3 = 0.0.

The five questions selected in this project were:

| Question ID | Topic |
|---|---|
| g004 | Native Indian language requirement |
| g006 | Prescribed Class IX English textbook |
| g007 | Class IX English assessment marks |
| g017 | Class IX Mathematics curriculum planning |
| g018 | Class IX Social Science curriculum planning |

These questions were used for the remaining analysis.

## 3. Inspect retrieved chunks

For each question, inspect:

1. The hybrid retrieval candidate list.
2. The final reranked results.
3. The top-three results.
4. The top-five results.
5. The chunk IDs, source documents and scores.

The project implementation uses a top-10 hybrid candidate pool before reranking. Therefore, this analysis records the actual top-10 candidate pool rather than claiming that 20 candidates were inspected.

The official assignment illustrates a top-20 candidate pool, but the analysis must describe the implementation that was actually run.

Record which expected gold chunks appear in the candidate pool and whether they reach the final top three.

## 4. Inspect the LLM answer

For each question, examine the generated answer.

Check:

- Did the LLM answer the question?
- Was the answer correct?
- Was any important information missing?
- Did the answer abstain because the retrieved context was insufficient?
- Did the answer use evidence from the retrieved chunks?

In this project, the diagnostic answer was generated using the top-five retrieved context.

The existing `ask_rag()` integration had a result-format compatibility issue with `retrieve_v9()`. The diagnostic answer was therefore obtained separately, without changing the application code for this assignment.

## 5. Inspect the original corpus

Check the original source documents and locate the expected gold chunks.

For this project, the expected gold chunk IDs were:

| Question | Gold chunks |
|---|---|
| g004 | Curriculum #32 |
| g006 | English #86, #87 |
| g007 | English #88, #97 |
| g017 | Maths #1, #7, #8, #27 |
| g018 | Social Science #3, #8, #11 |

Verify whether the information needed to answer each question actually exists in the corpus.

Do not assume that a failed retrieval means the corpus is missing the answer.

## 6. Diagnose the root cause

Use the assignment's decision flow:

**Question 1: Is the answer present in the corpus?**

- No → Corpus gap.
- Yes → Continue.

**Question 2: Was the answer-bearing chunk in the pre-rerank candidate pool?**

- No → Retrieval failure.
- Yes → Continue.

**Question 3: Did the correct chunk reach the final top three?**

- No → Reranker failure, a subtype of retrieval failure.
- Yes → Continue.

**Question 4: Did the LLM produce a wrong or incomplete answer despite receiving the correct chunk?**

- Yes → Generation failure.
- No, but it answered a different valid interpretation → Question ambiguity.

For this implementation, use the actual top-10 candidate pool when answering Question 2.

## 7. Propose a specific fix

The assignment requires a proposed fix, not implementation of that fix.

Examples:

| Root cause | Possible fix |
|---|---|
| Retrieval failure | Review tokenisation, chunk boundaries or embeddings |
| Reranker failure | Evaluate reranker behaviour and improve candidate ranking |
| Generation failure | Improve the prompt or evaluate another LLM |
| Question ambiguity | Reformulate the question or add clarification |
| Corpus gap | Add the missing source document or handle unavailable information explicitly |

The proposed fix must address the diagnosed problem rather than simply adding another retrieval technique.

## 8. Prepare the failure analysis report

Create:

`docs/wk9-failure-analysis.md`

Include five question sections.

Each section should contain:

1. Question ID and question.
2. Gold source.
3. Top-three retrieved chunks.
4. LLM answer.
5. Whether the gold chunk appeared in the pre-rerank candidates.
6. Whether the gold chunk appeared in the final top three.
7. LLM answer quality.
8. Root cause.
9. Explanation of the diagnosis.
10. Proposed fix.
11. Confidence in the diagnosis.

Finish with a **Pattern Summary** identifying the most common root cause and the highest-leverage improvement suggested by the five cases.

## 9. Accuracy checks

Before submitting, verify:

- All five selected questions are included.
- Retrieved chunk IDs and scores reflect actual results.
- Gold chunk IDs are checked against the corpus.
- The LLM answer is recorded accurately.
- The root cause follows the decision flow.
- Proposed fixes address the identified causes.
- The candidate pool is described accurately as top-10.
- The pattern summary is included.

Do not report assumed measurements or results as actual observations.

## 10. Final project files

| File | Purpose |
|---|---|
| `docs/wk9-failure-analysis.md` | Completed assignment report |
| `guides/Week9_Failure_Analysis_Step_by_Step_Guide.md` | This step-by-step learning and implementation guide |

The original assignment document remains the authority for the activity requirements.

## 11. GitHub submission

From the repository root:

```bash
git add Week9/guides/Week9_Failure_Analysis_Step_by_Step_Guide.md
git commit -m "Add Week 9 failure analysis step-by-step guide"
git push origin Main
```

This adds the missing guide without changing the already committed Week 9 implementation and assignment report.