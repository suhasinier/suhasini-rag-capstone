# Mini Project 1 — Prompt Strategy Comparison

## Performance Comparison

The four prompting strategies were tested on the same 10 job snippets, resulting in **40 main LLM calls** (10 snippets × 4 strategies).

| Strategy   | Accuracy (mean of 3) | Parse Rate | LLM Judge Score | Total Cost ($) | Latency p50 (s) |
| ---------- | -------------------: | ---------: | --------------: | -------------: | --------------: |
| Few-shot   |                  2.8 |       1.00 |             3.5 |         0.0006 |          1.4541 |
| Structured |                  2.8 |       1.00 |             3.5 |         0.0004 |          1.4496 |
| Zero-shot  |                  2.7 |       1.00 |             3.4 |         0.0004 |          1.4864 |
| CoT        |                  2.6 |       1.00 |             3.4 |         0.0011 |          2.5621 |

## Key Observations

* **Few-shot and Structured** achieved the highest mean accuracy: **2.8 out of 3**.
* **All four strategies achieved a 100% parse rate** in the final run.
* Few-shot and Structured also had the highest LLM judge score: **3.5**.
* Structured had a lower total cost than Few-shot in this run.
* Zero-shot had slightly lower accuracy at **2.7**, while keeping cost low.
* CoT had the lowest accuracy among the four strategies at **2.6**.
* CoT also had the highest median latency (**2.5621 seconds**) and highest total cost (**$0.0011**).
* The final run successfully completed all **40 main LLM calls**.

## Important Evaluation Cases

### J05 — No prior experience

The job posting says that fresh graduates are welcome and that no prior experience is required.

* Golden value: `0`
* `0` years is therefore the correct extraction.
* Returning `null` is not correct for this case because the posting explicitly indicates that no prior experience is required.

### J08 — Written number

The posting states **"Five years"** of UX research experience.

* Golden value: `5`
* The written number must be interpreted as the integer `5`.

### J09 — Experience range

The posting states **"Three to five years"**.

* Golden value: `3`
* The project convention is to use the **minimum value** from a range.
* Therefore, `3` is the expected extraction.

### J10 — Missing specific requirement

The posting explicitly says that a specific years requirement is not listed.

* Golden value: `null`
* The model should return `null` rather than inventing a number.
* The structured prompt was updated to explicitly instruct the model not to infer or guess when the information is not stated.

## Normalisation

The accuracy comparison applies basic normalisation to text fields by:

* removing leading and trailing whitespace
* comparing text without case differences

Punctuation is **not** removed by the current scoring function. This was relevant in J02, where one response contained `Northwind Ltd.` while the golden answer was `Northwind Ltd`. The punctuation difference therefore affected the exact field match.

This showed me that evaluation rules can affect the measured accuracy. For this project, I kept the scoring consistent with the implemented normalisation rather than changing the results after the experiment.

Other extraction differences were checked against the project's golden-set conventions, including written numbers, experience ranges, and zero years of experience.

## Overall Finding

Few-shot and Structured prompting produced the highest observed accuracy and judge scores in this run. Structured prompting achieved the same accuracy and judge score as Few-shot while using less total cost in this experiment. The results also show that prompt design affects extraction quality, output consistency, latency, and cost, so accuracy alone should not be considered in isolation.
