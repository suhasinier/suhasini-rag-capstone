# Mini Project 1 — Prompt Strategy Comparison

## 1. Which strategy performed best?

In this experiment, few-shot prompting had the highest mean accuracy, with a score of 2.8 out of 3. It also had a 100% parse rate. Structured and zero-shot prompting both had an accuracy of 2.6 out of 3, while CoT had 0 accuracy and a 0% parse rate.

Few-shot and zero-shot had the same LLM judge score of 3.3, so the main difference I observed was in the accuracy score.

## 2. What surprised me?

The most surprising result was the CoT strategy. I expected asking the model to think step by step might help with the extraction task. Instead, all 10 CoT responses failed to parse in my experiment.

I checked the CoT results separately in the notebook using:

```python
cot_results = df[df['strategy'] == 'cot']

cot_results[['snippet_id', 'raw_response', 'parsed',
             'accuracy', 'parse_success']]
```

For all 10 snippets, parsed was None, accuracy was 0, and parse_success was False. This resulted in a 0% parse rate and 0.0 mean accuracy for CoT.

This made me realize that for a task requiring a strict JSON output, adding step-by-step reasoning can sometimes cause problems with the required output format.

## 3. Which strategy would I use for my capstone?

For my Enterprise Knowledge Assistant (EKA), I would start with few-shot prompting. In this experiment, few-shot gave the highest mean accuracy of 2.8 out of 3 and a 100% parse rate. I would then test it with some representative questions from my capstone before making a final decision.

## 4. What would I try next?

If I had another day, I would test more examples and try improving the CoT prompt so that the reasoning does not interfere with the required JSON output. I would also compare the revised prompt with the few-shot prompt on the additional examples to see whether the results remain consistent.
