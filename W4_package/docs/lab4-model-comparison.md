# Lab 4 — Model comparison: gpt-4o-mini vs gpt-4o

**Cohort member:** _Suhasini Ramachandran_
**Date:** _25/09/2026_

## Numbers (filled in by `scripts/compare_models.py`)

```
Model            n    Total $     Avg $/q     Time
---------------------------------------------------
gpt-4o-mini     10    0.000765   0.000077    16.29s
gpt-4o          10    0.015108   0.001511    18.69s
```

> gpt-4o cost 19.7 × more than gpt-4o-mini on the same questions.

## Two-paragraph eyeball reflection

### Paragraph 1 — where the gap mattered

Across the 10 questions, the two models produced broadly similar answers for many of the basic conceptual questions. The differences were more noticeable on questions about production timeouts, schema versioning, tokens versus words, and tool-calling, where the gpt-4o responses sometimes provided different wording or additional detail. For example, the gpt-4o answer about production timeouts explicitly described an “Inference Timeout,” while the gpt-4o-mini answer used the term “Response Time Limit.” The schema-versioning question also showed a difference in how the two models interpreted the requested change. Overall, the side-by-side results did not show a consistent difference across all 10 questions.

### Paragraph 2 — your rough rule for when to reach for the bigger model

Based on this small 10-question comparison, I would consider gpt-4o for questions where additional reasoning or detail is important and the extra cost can be justified. For straightforward conceptual questions, the two answers were often quite similar in the snippets inspected. The measured total cost was $0.000765 for gpt-4o-mini versus $0.015108 for gpt-4o, so the cost difference should be considered when choosing the model. The comparison provides evidence from these 10 questions, but it is not enough by itself to generalize to every workload.

## Confidence calibration (optional)

The lab pipeline asks the model to return a `confidence` value in `[0, 1]`.
Skim the persisted rows in SQLite:

```bash
sqlite3 data/answers.db \
  "SELECT model, AVG(confidence), AVG(cost_usd) FROM answers GROUP BY model;"
```

The two models reported somewhat similar confidence values, with average confidence of 0.927 for gpt-4o and 0.900 for gpt-4o-mini across the 10 questions.
