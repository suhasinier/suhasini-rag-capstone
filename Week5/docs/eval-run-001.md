# Evaluation Run 001 — M1 Baseline

## 1. Run Information

- **Evaluation label:** `baseline-001`
- **Golden set:** `data/golden_set.jsonl`
- **Number of entries:** 20
- **Candidate model:** `gpt-4o-mini`
- **Judge model:** `gpt-4o`
- **Database:** `data/answers.db`
- **Evaluation script:** `scripts/run_eval.py`

This evaluation establishes the first measurement baseline for the Week 5 capstone. Each golden-set question was sent to the W4 `/ask_batched` endpoint, and the resulting candidate answer was evaluated by the LLM judge against the corresponding ideal answer.

---

## 2. Aggregate Results

| Metric | Score |
|---|---:|
| Average Accuracy | **3.50 / 4** |
| Average Groundedness | **3.50 / 4** |
| Average Format | **3.85 / 4** |
| Entries scored | **20** |

### Accuracy distribution

| Accuracy score | Number of entries |
|---|---:|
| 4 | 13 |
| 3 | 5 |
| 2 | 1 |
| 1 | 1 |

The candidate system performed strongly overall, particularly on response format. Most questions received an accuracy score of 4, while the harder and edge questions exposed some limitations.

---

## 3. Per-Entry Results

| ID | Accuracy | Groundedness | Format |
|---|---:|---:|---:|
| g001 | 4 | 4 | 4 |
| g002 | 4 | 4 | 4 |
| g003 | 4 | 4 | 4 |
| g004 | 4 | 4 | 4 |
| g005 | 4 | 4 | 4 |
| g006 | 3 | 3 | 4 |
| g007 | 4 | 4 | 4 |
| g008 | 4 | 4 | 4 |
| g009 | 4 | 4 | 4 |
| g010 | 4 | 4 | 4 |
| g011 | 4 | 4 | 4 |
| g012 | 4 | 4 | 4 |
| g013 | 3 | 3 | 4 |
| g014 | 3 | 3 | 4 |
| g015 | 4 | 4 | 4 |
| g016 | 3 | 3 | 4 |
| g017 | 3 | 3 | 4 |
| g018 | 4 | 4 | 4 |
| g019 | 1 | 1 | 2 |
| g020 | 2 | 2 | 3 |

---

## 4. What the Baseline Shows

### Where the system is strong

The system performed well on the majority of the happy-path questions.

Questions such as competency-based education, education frameworks, student participation, and learner-centred teaching received strong scores. The format score was also consistently high, with an average of 3.85/4.

The results suggest that the current W4 candidate can produce clear and relevant answers for questions that are closely aligned with the knowledge domain represented by the golden set.

### Where the system is weaker

The lower scores occur mainly on questions requiring more detailed reasoning and on the two edge cases.

The harder questions g006, g013, g014, g016 and g017 received accuracy and groundedness scores of 3 rather than 4.

The two edge cases were weaker:

- **g019:** Accuracy 1, Groundedness 1, Format 2
- **g020:** Accuracy 2, Groundedness 2, Format 3

These questions test whether the system can recognize when a question is outside the intended knowledge scope rather than producing a plausible answer.

---

## 5. Judge Spot-Check

Five randomly selected entries were manually reviewed:

- g004
- g009
- g011
- g017
- g018

The candidate answers, ideal answers, scores, and judge reasoning were compared.

The four 4/4/4 judgments reviewed (g004, g009, g011 and g018) appeared reasonable and were consistent with the ideal answers.

g017 received 3/3/4. This was also considered reasonable because the candidate answer was relevant and well formatted but introduced several specific assessment techniques that went beyond the tighter focus of the ideal answer.

No clear judge-score disagreements were identified in the five-entry spot-check.

The spot-check therefore did not reveal evidence that the judge rubric was systematically too lenient for this baseline run.

---

## 6. What We Will Improve

Before the next evaluation iteration, the main areas to investigate are:

1. Improve handling of harder questions that require connecting multiple concepts or conditions.
2. Improve refusal and out-of-scope behaviour for edge questions so that the system does not provide unsupported answers.
3. Continue using the same golden set and judge rubric for subsequent comparisons so that changes can be measured consistently against this baseline.

---

## 7. Baseline Conclusion

The Week 5 baseline provides a first quantitative measurement of the W4 candidate system.

**Baseline:**

- Accuracy: **3.50 / 4**
- Groundedness: **3.50 / 4**
- Format: **3.85 / 4**
- Evaluation size: **20 questions**

The baseline is stored in the SQLite `eval_runs` table under the label `baseline-001`.

Future prompt, retrieval, or model changes should be evaluated against this baseline so that improvements can be measured rather than judged only by individual examples.