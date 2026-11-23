# W9 Failure Analysis

5 questions where hybrid_rerank still failed.

Root cause categories: retrieval / reranker / generation / question / corpus.

**Diagnostic note:** The current Week 9 implementation uses 10 hybrid candidates before cross-encoder reranking (`k_final=10`). Therefore, the pre-rerank checks below refer to the actual top 10 candidates produced by this implementation, not the top 20 mentioned in the assignment's sample template.

---

## Question 1 (id: golden_set_question_g004)

**Question:** What does the curriculum say about choosing R3 when a student has not studied a native Indian language in Classes VI to VIII?

**Gold source:** Curriculum_SecP1_2026-27.pdf

**Expected gold chunk:** Curriculum_SecP1_2026-27#32

**Top-3 retrieved:**

1. Curriculum_SecP1_2026-27.pdf / section: Curriculum_SecP1_2026-27 / chunk #107 / rerank score: 1.9942
2. Curriculum_SecP1_2026-27.pdf / section: Curriculum_SecP1_2026-27 / chunk #35 / rerank score: 1.6435
3. Curriculum_SecP1_2026-27.pdf / section: Curriculum_SecP1_2026-27 / chunk #34 / rerank score: 1.5621

**LLM answer:**

For students who have not studied even one native Indian language in classes VI-VIII, a native Indian language will be compulsory for them in class IX [Curriculum_SecP1_2026-27#32].

**Was the gold chunk in candidates (pre-rerank top-20)?** Yes. It was found at position 3 in the actual top-10 hybrid candidate list.

**Was the gold chunk in top-3 after rerank?** No. It moved to position 4.

**LLM answer quality given retrieved chunks:** OK. The diagnostic LLM call used the top 5 reranked chunks, which included the gold chunk at position 4, and produced the correct answer.

**Root cause:** reranker

**Why:** The hybrid stage retrieved the correct chunk at position 3, but the cross-encoder ranked it below three other chunks. The correct information was therefore excluded from the final top 3, although it remained available in the diagnostic top 5.

**Proposed fix:** Evaluate the cross-encoder on conditional and exception-based questions. Improve reranking so that chunks containing the exact rule and its conditions are promoted above generally related language-policy chunks.

**Confidence in diagnosis:** High

---

## Question 2 (id: golden_set_question_g006)

**Question:** What prescribed English textbook is listed for Class IX?

**Gold source:** English_LL_SecP1IX_2026-27.pdf

**Expected gold chunks:** English_LL_SecP1IX_2026-27#86 and #87

**Top-3 retrieved:**

1. ScienceSt_SecP1_2026-27.pdf / section: ScienceSt_SecP1_2026-27 / chunk #58 / rerank score: 5.6165
2. Curriculum_SecP1_2026-27.pdf / section: Curriculum_SecP1_2026-27 / chunk #24 / rerank score: 4.6495
3. Curriculum_SecP1_2026-27.pdf / section: Curriculum_SecP1_2026-27 / chunk #35 / rerank score: 4.4650

**LLM answer:**

The provided context does not specify a prescribed English textbook for Class IX.

**Was the gold chunk in candidates (pre-rerank top-20)?** Yes. Chunk #86 was at position 1 in the actual top-10 hybrid candidate list. Chunk #87 was not in that candidate list.

**Was the gold chunk in top-3 after rerank?** No. Neither expected chunk appeared in the final top 3 or top 5.

**LLM answer quality given retrieved chunks:** Incomplete. The answer correctly avoided inventing a textbook name, but the correct source chunk had already been retrieved before reranking.

**Root cause:** reranker

**Why:** The hybrid stage placed the correct English textbook chunk first, but the cross-encoder removed it from even the top 5. It ranked unrelated Science and general curriculum chunks above the exact English textbook information.

**Proposed fix:** Evaluate reranking on short factual questions that require an exact named entity, such as a textbook title. Add a reranker evaluation set that checks whether exact answer-bearing chunks remain in the top 3.

**Confidence in diagnosis:** High

---

## Question 3 (id: golden_set_question_g007)

**Question:** How are marks divided between the Class IX English written examination and internal assessment?

**Gold source:** English_LL_SecP1IX_2026-27.pdf

**Expected gold chunks:** English_LL_SecP1IX_2026-27#88 and #97

**Top-3 retrieved:**

1. Curriculum_SecP1_2026-27.pdf / section: Curriculum_SecP1_2026-27 / chunk #144 / rerank score: 5.0808
2. Curriculum_SecP1_2026-27.pdf / section: Curriculum_SecP1_2026-27 / chunk #154 / rerank score: 4.3380
3. SocialScience_SecP1IX_2026-27.pdf / section: SocialScience_SecP1IX_2026-27 / chunk #111 / rerank score: 3.5114

**LLM answer:**

In Class IX, the marks are divided as follows: the written examination consists of 80 marks, and the internal assessment is worth 20 marks. The total for English is 100 marks, with the breakdown being 20 marks for reading skills, 30 marks for writing skills and grammar, 30 marks for language through literature, and 20 marks for internal assessment [Curriculum_SecP1_2026-27#144][English_LL_SecP1IX_2026-27#98].

**Was the gold chunk in candidates (pre-rerank top-20)?** Yes. Expected chunk #88 appeared at position 6 and #97 at position 9 in the actual top-10 hybrid candidates.

**Was the gold chunk in top-3 after rerank?** No. Neither expected chunk appeared in the final top 3 or top 5.

**LLM answer quality given retrieved chunks:** OK for the requested overall 80/20 split. The answer also supplied the section-wise breakdown using English chunk #98, which appeared at position 10 before reranking and position 5 after reranking. The expected chunks #88 and #97 were not retained.

**Root cause:** reranker

**Why:** The correct English assessment chunks were retrieved by the hybrid stage but were ranked below general curriculum chunks. The LLM nevertheless produced the correct overall marks split using the general curriculum chunk and another English syllabus chunk.

**Proposed fix:** Improve subject-specific reranking so that a question about English assessment prioritises English syllabus chunks over general curriculum assessment information when both are relevant. Evaluate both exact answer accuracy and source-specific retrieval accuracy.

**Confidence in diagnosis:** High

---

## Question 4 (id: golden_set_question_g017)

**Question:** A school wants to check whether its Class IX Mathematics plan covers the required content and supports students' mathematical thinking. What should it compare?

**Gold source:** Maths_SecP1IX_2026-27.pdf

**Expected gold chunks:** Maths_SecP1IX_2026-27#1, #7, #8 and #27

**Top-3 retrieved:**

1. Maths_SecP1IX_2026-27.pdf / section: Maths_SecP1IX_2026-27 / chunk #0 / rerank score: 1.0378
2. Maths_SecP1IX_2026-27.pdf / section: Maths_SecP1IX_2026-27 / chunk #87 / rerank score: -0.4934
3. Curriculum_SecP1_2026-27.pdf / section: Curriculum_SecP1_2026-27 / chunk #109 / rerank score: -0.6149

**LLM answer:**

The school should compare its Class IX Mathematics plan with the revised syllabus that emphasizes developing core mathematical competencies, including problem-solving, visualization, mathematical modeling, mathematical communication, computational thinking, and data analytics [Maths_SecP1IX_2026-27#1]. Additionally, it should ensure that the plan aligns with the guidelines for Mathematics as outlined in the NCERT and CBSE publications [Maths_SecP1IX_2026-27#87].

**Was the gold chunk in candidates (pre-rerank top-20)?** Yes, partially. Expected chunks #1 and #7 appeared at positions 6 and 7 in the actual top-10 hybrid candidates. Expected chunks #8 and #27 were not retrieved in that candidate list.

**Was the gold chunk in top-3 after rerank?** No. Expected chunk #1 appeared at position 5 in the reranked top 5, while the other expected chunks did not appear there.

**LLM answer quality given retrieved chunks:** Incomplete. The LLM identified mathematical competencies from chunk #1, but did not adequately cover the required content and unit structure represented in the other expected chunks.

**Root cause:** reranker

**Why:** The hybrid candidate pool contained Maths chunks #1 and #7, but the reranker did not place either in the final top three. Other expected chunks (#8 and #27) were not present in the top-10 candidate pool. This indicates a reranking problem for the chunks that were retrieved, alongside a candidate-coverage limitation.

**Proposed fix:** Evaluate reranking on multi-part questions that require both syllabus content and competencies. Also investigate query decomposition or broader candidate retrieval so that separate aspects of a question can retrieve complementary chunks. These changes should be evaluated before adoption.

**Confidence in diagnosis:** Medium

---

## Question 5 (id: golden_set_question_g018)

**Question:** How can a teacher use the Class IX Social Science syllabus to plan learning across its different subject areas without treating the course as only a list of facts?

**Gold source:** SocialScience_SecP1IX_2026-27.pdf

**Expected gold chunks:** SocialScience_SecP1IX_2026-27#3, #8 and #11

**Top-3 retrieved:**

1. Curriculum_SecP1_2026-27.pdf / section: Curriculum_SecP1_2026-27 / chunk #96 / rerank score: 2.0229
2. Curriculum_SecP1_2026-27.pdf / section: Curriculum_SecP1_2026-27 / chunk #144 / rerank score: -0.9376
3. SocialScience_SecP1IX_2026-27.pdf / section: SocialScience_SecP1IX_2026-27 / chunk #0 / rerank score: -1.0938

**LLM answer:**

The context does not provide specific strategies or methods for a teacher to use the Class IX Social Science syllabus to plan learning across its different subject areas. Therefore, I cannot answer the question based on the provided information.

**Was the gold chunk in candidates (pre-rerank top-20)?** Yes, partially. Expected chunks #11 and #3 appeared at positions 2 and 8 in the actual top-10 hybrid candidate list. Expected chunk #8 was not retrieved.

**Was the gold chunk in top-3 after rerank?** No. Expected chunk #3 appeared at position 5 in the reranked top 5. Expected chunk #11 was pushed out of the top 5.

**LLM answer quality given retrieved chunks:** Incomplete. The LLM appropriately abstained because the final retrieved context did not contain enough information to address the question's different subject areas and learning expectations.

**Root cause:** reranker

**Why:** The hybrid candidate pool contained Social Science chunks #11 and #3, but the reranker did not place either in the final top three. Expected chunk #8 was not present in the top-10 candidate pool. This indicates a reranking problem for the retrieved chunks, alongside a candidate-coverage limitation.

**Proposed fix:** Improve retrieval coverage for synthesis questions and evaluate whether reranking preserves complementary chunks from the same subject syllabus. Query decomposition could be tested to retrieve the disciplinary structure and learning aims separately.

**Confidence in diagnosis:** Medium

---

## Pattern summary

Across the 5 failures, the most common root cause was: **reranker**.

In all five cases, at least one expected answer-bearing chunk was present in the actual hybrid top-10 candidate list, but none of the expected gold chunks reached the final top 3. The reranker therefore had a major role in the observed precision@3 failures.

Two synthesis questions, g017 and g018, also showed incomplete candidate coverage: some expected chunks were not present even before reranking.

This suggests the highest-leverage fix for the capstone is: **improve reranker evaluation and ranking for exact factual questions, subject-specific questions, and multi-part synthesis questions.** Candidate coverage should also be measured for questions that need multiple chunks. The diagnostic results do not justify adding another retrieval technique without first evaluating these targeted changes.

---

## Implementation note

The assignment template refers to pre-rerank top-20 candidates. The current Week 9 `hybrid_retrieve()` implementation uses `k_final=10`, so this analysis records top-10 candidate membership. The top-3 and top-5 rankings were inspected separately.

The `section_path` metadata returned by Qdrant was document-level for these chunks; it did not provide more specific subsection names.
