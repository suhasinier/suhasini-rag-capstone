# DR #1 Summary — M1

## 1. What You Built

This capstone is an AI-powered education and curriculum assistant designed primarily for CBSE school teachers who need quick access to information from CBSE/NCERT curriculum, assessment, learning-outcome, and education-framework documents. The goal is to reduce the time spent manually searching multiple documents and provide concise answers grounded in the relevant evidence. By M1, the W4 `/ask`, `/ask_batched`, and `/health` API foundation is in place, along with a 20-entry golden set and an evaluation layer using LLM-as-judge, pairwise prompt comparison, and a Critic-Creator experiment. The current system provides an evaluation baseline that will be used to measure the impact of retrieval and later RAG improvements.

## 2. What You Measured

The W5 baseline evaluated all 20 golden-set questions using the LLM-as-judge rubric. The average accuracy was **3.50/4.00**, average groundedness was **3.50/4.00**, and average format score was **3.85/4.00**. Accuracy scores were 4 for 13 entries, 3 for 5 entries, 2 for 1 entry, and 1 for 1 entry. The weaker results were concentrated mainly in harder and edge questions, particularly g019 and g020. A pairwise comparison between Prompt V1 and V2 produced 2 V1 wins, 0 V2 wins, 10 ties, and 8 ambiguous results, with a 40% position-bias indicator. Therefore, the pairwise experiment is treated as inconclusive rather than as evidence that V1 is definitively better. The Critic-Creator experiment on g019 converged in Round 1 with a 4/4/4 score.

## 3. Top 3 Things I Want to Discuss

1. **Evaluation:** Are the current accuracy and groundedness results strong enough to serve as the M1 baseline, or should the rubric be refined before later retrieval experiments?

2. **Prompt comparison:** Given the 40% position-bias indicator and the large number of ambiguous results, what additional pairwise methodology would make future prompt comparisons more trustworthy?

3. **RAG improvement:** Which retrieval strategy should be prioritised in the next phase to improve the weaker answers on harder and edge questions without increasing cost significantly?

## 4. What I’ll Defend If Asked

- **Why gpt-4o-mini?** W4 showed broadly similar answer quality compared with gpt-4o while costing substantially less, so gpt-4o-mini is the default model and gpt-4o can be reserved for harder cases.

- **Why a 20-question golden set?** The golden set provides a fixed, representative evaluation baseline covering happy-path, harder, and edge questions so that later improvements can be measured consistently.

- **Why not claim the new prompt won?** The pairwise experiment produced no V2 wins and showed 40% position bias with 8 ambiguous cases. Therefore, the responsible conclusion is that the experiment is inconclusive rather than claiming a definitive prompt winner.