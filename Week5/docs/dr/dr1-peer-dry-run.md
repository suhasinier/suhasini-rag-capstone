# DR #1 Peer Dry-Run Notes

- **Date:** 2026-10-06
- **Type:** Simulated peer dry-run
- **Reason:** A cohort peer was not available, so the DR #1 questions were simulated before the actual Design Review.

## 1. Presentation

Presented the M1 capstone summary covering:

- The target user: CBSE school teachers.
- The problem: manually searching CBSE/NCERT documents for curriculum, assessment, and learning-outcome information.
- The proposed solution: an AI-powered education and curriculum assistant.
- The W5 evaluation approach: LLM-as-judge, pairwise comparison, and Critic-Creator.
- The M1 evaluation baseline and current limitations.

## 2. Simulated Reviewer Questions

### Q1. Why did you choose gpt-4o-mini instead of gpt-4o?

**Answer:**

We compared both models in Week 4. The answers were broadly similar, but gpt-4o-mini was significantly cheaper — approximately $0.000765 for 10 questions compared with $0.015108 for gpt-4o. Therefore, I chose gpt-4o-mini as the default because it provides a better cost-quality balance. For harder cases where the smaller model may not be sufficient, gpt-4o can still be considered.

**Assessment:** Answered cleanly.

### Q2. Your evaluation baseline has an average accuracy of 3.50/4.00. Does that mean the system is ready for production?

**Answer:**

No. The 3.50/4.00 score is an M1 baseline, not evidence that the system is production-ready. Most questions performed reasonably well, but some harder and edge questions, particularly g019 and g020, scored much lower. The purpose of the later RAG work is to improve these results, especially groundedness and accuracy, and measure the improvement against the same golden set.

**Assessment:** Answered cleanly.

### Q3. Your pairwise experiment did not show a clear winner. Why didn't you simply choose Prompt V1 or V2?

**Answer:**

I did not want to make a decision from weak evidence. V1 had 2 wins, V2 had 0 wins, but there were also 10 ties and 8 ambiguous cases, with a 40% position-bias indicator. Therefore, the experiment is inconclusive rather than strong evidence that V1 is better. A better-controlled comparison with more evidence would be needed before locking the prompt decision.

**Assessment:** Answered cleanly.

## 3. Dry-Run Outcome

All three simulated questions could be answered using the evidence from the W4 and W5 work.

No new unresolved question was identified during this simulated dry-run, so no additional change was made to ADR Section 9.

## 4. Follow-up

The actual DR #1 session should be treated as the formal peer/reviewer discussion. Any genuinely unresolved questions or decisions raised during that session should be added to the ADR's Open Questions or Change Log as appropriate.