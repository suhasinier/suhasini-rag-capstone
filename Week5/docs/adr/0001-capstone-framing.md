# ADR-0001: Capstone Framing — AI-Powered Education & Curriculum Assistant

- **Status:** v1 — Locked
- **Date:** 2026-10-06
- **Author:** Suhasini Ramachandran
- **Milestone:** M1 / DR #1

## 1. Context

This capstone aims to build an AI-powered assistant that helps CBSE school teachers understand and work with CBSE/NCERT curriculum, assessment, learning-outcome, and education-framework documents.

The primary user is a CBSE school teacher who needs to quickly find and understand information from these documents while planning lessons and assessments. The current workflow requires manually searching CBSE and NCERT websites, curriculum documents, PDFs, circulars, and assessment guidelines. Finding the relevant document or section can take approximately 5–10 minutes per question, followed by additional time to read and interpret the information.

The system is intended to provide concise, document-grounded answers instead of relying only on general LLM knowledge. When sufficient supporting information is unavailable, the system should indicate uncertainty rather than invent an answer.

The capstone therefore focuses on reliable question answering over an education-document domain, with evaluation and evidence used to guide subsequent engineering decisions.

## 2. Decision — Solution Framing

The capstone will operate as a document-grounded AI assistant for CBSE/NCERT education-related questions.

| Solution element | Decision |
|---|---|
| **Inputs** | A user provides a natural-language question about CBSE/NCERT curriculum, learning outcomes, assessment, or education frameworks. |
| **Outputs** | The system produces a concise, grounded answer based on the relevant education documents, with source references where possible. |
| **Tools** | The system uses an OpenAI language model and will add a retrieval component over the selected CBSE/NCERT document corpus in later weeks. |
| **Memory** | Version 1 does not retain information between separate user sessions; each question is treated independently. |
| **Autonomy level** | The system operates as a RAG-based Q&A assistant. It retrieves relevant information and generates an answer but does not independently take actions. |
| **Decision boundaries** | The system may answer questions supported by the relevant evidence. When sufficient evidence is unavailable or the question requires professional human judgment, it should clearly indicate uncertainty rather than invent an answer. |

## 3. Consequences

### Positive consequences

- Teachers can obtain information from multiple education documents more quickly.
- Grounding answers in source documents can reduce unsupported answers.
- The system provides a practical RAG engineering use case in the education domain.
- A fixed golden set and evaluation process provide a measurable baseline for future improvements.
- The API contract can continue evolving internally without unnecessarily breaking downstream consumers.

### Negative consequences and risks

- Answer quality depends on the quality and coverage of the underlying CBSE/NCERT documents.
- Incorrect retrieval can lead to incorrect or incomplete answers.
- The LLM may still produce unsupported information when evidence is insufficient.
- LLM-as-judge evaluation is itself model-based and can contain judge bias.
- Supporting evaluation and observability adds cost and implementation complexity.

### Things to revisit

- Retrieval quality and strategy will be revisited in later RAG weeks.
- Confidence and source handling will be improved as retrieval is introduced.
- Memory and more agentic behaviour may be considered later if the core Q&A system proves reliable.

## 4. Decisions Locked at M1

The following decisions are locked for the M1 baseline and are supported by W4 comparison results and W5 evaluation evidence.

| Decision | M1 evidence | Locked decision |
|---|---|---|
| **Default LLM model** | W4 comparison: `gpt-4o-mini` cost = **$0.000765 for 10 questions**; `gpt-4o` cost = **$0.015108 for 10 questions**. Answers were broadly similar. | Use **`gpt-4o-mini`** as the default model. `gpt-4o` remains available for harder questions or cases where the mini model is insufficient. |
| **Average cost budget** | W4 established a soft budget of **≤ $0.01 per `/ask_batched` call on average over 10 questions**. | Retain the **$0.01 average-call budget** as the cost guardrail. |
| **API schema** | W4 added `confidence`, `sources`, and `schema_version` additively while preserving W3 fields. | Retain **schema version `v1`** for additive changes. Breaking changes require `v2`, `v3`, etc. |
| **Baseline evaluation** | W5 eval-run-001 evaluated **20 golden questions** using LLM-as-judge. | Use the W5 eval-run-001 results as the **M1 evaluation baseline**. |
| **Prompt comparison** | Pairwise-001: V1 wins **2**, V2 wins **0**, ties **10**, ambiguous **8**; position-bias indicator **40%**. | Do **not** claim V2 is superior. Treat the pairwise result as inconclusive because of the high position-bias/ambiguity. |
| **Critic-Creator experiment** | g019 converged in **Round 1** with a **4/4/4** judge score. | Retain Critic-Creator as an experimental improvement mechanism; further evidence is required before treating it as a production mechanism. |

## 5. Sponsor KPIs

The following three KPIs are taken from the Week 5 Stakeholder Map.

| Sponsor KPI | M1 measurement | W12 target |
|---|---|---|
| **Time to answer** | Current manual workflow requires approximately **5–10 minutes of document searching per question**, plus interpretation time. | Reduce average time to **≤2 minutes per question**. |
| **Grounded answer quality** | W5 eval-run-001 average **groundedness = 3.50/4.00** and average **accuracy = 3.50/4.00** across 20 questions. | Reach **≥3.75/4.00 average groundedness** and maintain strong accuracy. |
| **Teacher adoption** | **Not yet measured at M1**; no teacher usage population has been instrumented yet. | Reach **≥50% of the defined target-teacher group using the assistant regularly**. |

Teacher adoption is therefore a KPI with a baseline still to be established. The target is a W12 target, not a claim about current usage.

## 6. Evaluation Baseline

The W5 `eval-run-001` baseline evaluated 20 golden-set entries using the LLM-as-judge rubric.

| Metric | M1 baseline |
|---|---:|
| **Entries evaluated** | 20 |
| **Average accuracy** | **3.50 / 4.00** |
| **Average groundedness** | **3.50 / 4.00** |
| **Average format** | **3.85 / 4.00** |
| **Accuracy = 4** | 13 entries |
| **Accuracy = 3** | 5 entries |
| **Accuracy = 2** | 1 entry |
| **Accuracy = 1** | 1 entry |
| **Wall-clock evaluation time** | **81.0 seconds** |

The strongest baseline dimensions were format and the majority of accuracy scores. The main weaknesses were concentrated in the harder and edge questions, especially g019 and g020.

The baseline is therefore sufficient to serve as an M1 measurement point, but it is not evidence that the system is production-ready.

## 7. Evaluation and Improvement Approach

W5 establishes three complementary evaluation mechanisms.

### LLM-as-judge

The judge evaluates an answer against the ideal answer on three dimensions:

- Accuracy
- Groundedness
- Format

The judge provides an absolute quality measurement for the current system.

### Pairwise comparison

Two prompt variants were compared using forward and reversed answer positions to reduce the risk of position bias.

The tested change was the addition of a source-citation requirement to Prompt V2.

The result was:

- V1 wins: 2
- V2 wins: 0
- Tie: 10
- Ambiguous: 8
- Position-bias indicator: 40%

Therefore, no strong prompt decision is made from this experiment alone.

### Critic-Creator

The Critic-Creator experiment was run on hard golden entry g019.

The process generated a candidate answer, evaluated it, and stopped when the answer exceeded the configured threshold. g019 reached 4/4/4 in Round 1 and therefore did not require additional critic rounds.

This demonstrates the mechanism but does not yet establish production-level reliability.

## 8. API, Model and Schema Constraints

The W3/W4 API contract remains the foundation for the capstone.

### Endpoints

- `POST /ask`
- `POST /ask_batched`
- `GET /health`

### Answer contract

The W3 fields remain:

- `content`
- `cost_usd`
- `retries`

W4 added:

- `confidence`
- `sources`
- `schema_version`

The current schema is `v1`.

Additive changes with optional defaults remain within `v1`. Breaking changes such as removing or renaming required fields, changing field types, making optional fields required, or changing the semantic meaning of an existing field require a new schema version.

When a new schema version is introduced, the existing version remains the default during the transition period according to the W4 API contract.

The cost budget remains a soft observability guardrail rather than a hard rejection rule.

## 9. Open Questions

The following questions remain unresolved and should be revisited during later weeks and the design reviews:

1. **How much will retrieval improve groundedness and accuracy?**  
   The W5 baseline is based on the current system; the effect of adding actual document retrieval will be measured in later RAG weeks.

2. **What retrieval strategy will provide sufficient evidence for harder and multi-section questions?**  
   The current evaluation identifies weaker performance on harder questions, but the best chunking, retrieval and ranking strategy is not yet known.

3. **How should confidence and source references be calibrated for production use?**  
   The API already supports `confidence` and `sources`, but their reliability and usefulness need to be validated once retrieval is introduced.

These questions are intentionally left open rather than being resolved without evidence.

## 10. DR #1 Defence

**Leave this section blank until the live DR #1 session.**

During DR #1, record:

- Questions asked by reviewers
- Evidence used to defend the decision
- Decisions that reviewers challenged
- Any changes or follow-up actions agreed during the review

No silent changes should be made to the locked ADR after M1. Any agreed future change should be recorded in the change log.

## 11. Change Log

| Version / Week | Change | Reason |
|---|---|---|
| **W1 — v0 Draft** | Created the initial capstone framing for an AI-powered CBSE/NCERT education and curriculum assistant. | Establish the initial problem, inputs, outputs, tools, memory, autonomy level, and decision boundaries. |
| **W4** | Added model, cost-budget, API schema-versioning and additive `Answer` fields including `confidence`, `sources`, and `schema_version`. | Strengthen the API contract and establish evidence-based model/cost decisions before M1. |
| **W5 — v1 Locked** | Added Stakeholder Map alignment, M1 decisions, sponsor KPIs, W5 evaluation baseline, evaluation/improvement approach, open questions and DR #1 defence area. | Lock the Phase-1 design using stakeholder and evaluation evidence and prepare the capstone for DR #1. |

**Locked status:** This ADR is the M1 v1 decision record. Future changes should be made deliberately and recorded in this change log with the reason for the change.