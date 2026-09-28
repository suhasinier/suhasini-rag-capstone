# Mini Project 1 — Prompt Strategy Comparison

## Project Overview

This project compares four prompting strategies for extracting information from job postings:

1. Zero-shot
2. Few-shot
3. Structured
4. Chain-of-thought (CoT)

The task is to extract three fields:

* `company`
* `role`
* `years_experience_required`

The project uses the 10 provided job snippets and the provided golden dataset for evaluation.

## Project Files

| File                                 | Purpose                                                         |
| ------------------------------------ | --------------------------------------------------------------- |
| `learner/MP1_Starter_Template.ipynb` | Completed notebook containing the end-to-end implementation     |
| `mp1_comparison.md`                  | Comparison of accuracy, parsing, judge score, cost, and latency |
| `mp1_writeup.md`                     | One-page reflection and findings                                |
| `requirements.txt`                   | Python packages required for the project                        |
| `data/job_snippets.jsonl`            | 10 job posting snippets                                         |
| `data/golden_set.jsonl`              | Golden reference answers                                        |

## How to Run

1. Open `learner/MP1_Starter_Template.ipynb` in the Vocareum environment.
2. Make sure the required Python packages are installed using `requirements.txt`.
3. Make sure the OpenAI API key is available in the environment.
4. Run the notebook cells in order.
5. The notebook runs the four prompting strategies on the 10 job snippets, resulting in 40 main LLM calls.
6. The notebook then scores the outputs and produces the comparison results.

The main model used for the four prompting strategies is `gpt-4o-mini`. The LLM-as-a-Judge step uses `gpt-4o`.

## Evaluation

Each extracted result is evaluated against the golden dataset using:

* Accuracy across the three extracted fields
* Parse success rate
* LLM-as-a-Judge score
* Total API cost
* Median response latency

The final comparison is available in `mp1_comparison.md`.

## Important Evaluation Rules

The evaluation follows the conventions provided with the project:

* `7+ years` is treated as `7`.
* `Around 6 years` is treated as `6`.
* For a range such as `3–5 years`, the minimum value `3` is used.
* If no specific years requirement is stated, the expected value is `null`.
* If the posting explicitly says no prior experience is required, the expected value is `0`.
* Text comparison applies basic normalisation for whitespace and letter case.

## Final Results

The final run completed all **40 main LLM calls**.

All four strategies achieved a **100% parse rate**.

The highest observed mean accuracy was **2.8 out of 3**, achieved by both Few-shot and Structured prompting.

The detailed results and observations are documented in `mp1_comparison.md`, and the reflection is provided in `mp1_writeup.md`.
