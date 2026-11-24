# W9 Stretch — Query rewriting trial

**Technique tried:** Step-back

**Reason for choice:** The W9 evaluation showed retrieval failures for some questions. Step-back was selected to test whether retrieving a broader version of a specific question could improve retrieval.

## Results

| Metric | Core (hybrid+rerank) | + Step-back | Delta |
|---|---:|---:|---:|
| Precision@3 | 0.556 | 0.556 | 0.000 |
| Precision@5 | 0.778 | 0.722 | -0.056 |
| Cost per query | Not measured | Not measured | Not measured |
| Latency p50 | Not measured | Not measured | Not measured |

## Verdict

- [ ] KEEP — precision lift justifies cost/latency
- [x] DROP — no meaningful improvement, not worth the extra LLM call
- [ ] KEEP BUT CONDITIONAL — only apply for a specific query pattern

## Reasoning

Step-back did not improve Precision@3. Both the core hybrid+rerank approach and Step-back achieved 0.556.

Precision@5 decreased from 0.778 to 0.722, a decline of 0.056.

The trial therefore did not demonstrate a retrieval-quality benefit from query rewriting. Since Step-back also introduces an additional LLM call, the added complexity and cost are not justified by these results.

Cost per query and latency p50 were not measured in this trial.