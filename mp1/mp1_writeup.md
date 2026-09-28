# Mini Project 1 — Prompt Strategy Comparison

## 1. Which strategy performed best?

* **Few-shot and structured prompting** had the highest mean accuracy: **2.8 out of 3**.
* **Zero-shot:** 2.7 out of 3.
* **CoT:** 2.6 out of 3.
* All four strategies achieved a **100% parse success rate**.
* Few-shot and structured had the highest **LLM-as-a-Judge score: 3.5/4**.
* Structured had a total cost of about **$0.0004** and a median latency of **1.4496 seconds**.
* Few-shot cost about **$0.0006**.
* CoT had the highest median latency at **2.5621 seconds**.
* Therefore, the experiment did not show one strategy winning every dimension. **Few-shot and structured performed best on accuracy, while structured had the lower cost with similar latency.**

## 2. What surprised me?

* The most important finding was the difference between **"no experience required"** and **"experience not stated."**
* **J05:** The posting says *"no prior experience required."*

  * Golden answer: **0 years**
  * All four strategies returned **null**.
  * This was a genuine extraction/interpretation failure.
* **J10:** The posting does not give a specific years requirement.

  * Golden answer: **null**
  * All four strategies correctly returned **null**.
  * This shows that the models could handle genuinely missing information correctly.
* **J09:** The posting says *"three to five years."*

  * The project rule is to use the **minimum value: 3**.
  * Structured returned **3** correctly.
  * Zero-shot, few-shot and CoT returned **null**.
* I also found a **normalisation issue** in J02 and J08:

  * The model returned **"Northwind Ltd."** instead of **"Northwind Ltd"**.
  * It also returned **"Wonka Confectionery Ltd."** instead of **"Wonka Confectionery Ltd"**.
  * The information was essentially correct, but our strict string comparison treated the punctuation difference as an error.
* CoT was also slower:

  * **CoT:** 2.5621 seconds median latency.
  * Other strategies: approximately **1.45–1.49 seconds**.
* These results showed me that prompt strategy affects not only accuracy, but also **handling of edge cases, output consistency, cost and latency**.

## 3. Which strategy would I use for my capstone?

* For my **AI-powered CBSE/NCERT curriculum and education-framework assistant**, I would start with the **structured approach**.
* My capstone needs:

  * Clear and consistent outputs.
  * Answers grounded in the available documents.
  * Minimal guessing when information is not available.
  * Reliable extraction of information from source documents.
* The structured strategy achieved:

  * **2.8/3 mean accuracy**
  * **100% parse success**
  * **3.5/4 LLM-judge score**
  * About **$0.0004 total cost**
  * **1.4496 seconds median latency**
* I would still test it with representative questions from my actual capstone before treating it as the final prompting strategy.

## 4. What would I try next?

* Test the prompts on a **larger set of examples**.
* Include more edge cases such as:

  * Information that is completely missing.
  * Explicitly stated zero values.
  * Ranges such as **3–5 years**.
  * Different ways of expressing the same information.
* Improve the **normalisation/scoring rules** so harmless punctuation differences do not reduce the accuracy score.
* Add an explicit instruction for cases such as:

  * **"No experience required" → 0**
  * **"Experience not stated" → null**
  * **"3–5 years" → 3**
* Test a structured prompt that explicitly says **not to infer information that is not supported by the source documents**.
* Compare the revised structured prompt with the few-shot approach on additional examples.
* Use the additional results to check whether the findings from this 10-job experiment remain consistent in the actual education domain.
