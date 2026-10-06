# Prompt Pairwise Comparison — Run 001

## 1. Experiment

This experiment compares two versions of the Enterprise Knowledge Assistant system prompt.

### Prompt V1

V1 instructs the assistant to:

- answer using only the retrieved context
- clearly state when the answer is not available in the context

### Prompt V2

V2 contains all V1 instructions and additionally requires:

- citation of the source section number when the answer comes from a specific policy document
- listing multiple source sections when applicable
- stating "(no citation available)" when no citation is available

The experiment was designed as a single-change prompt comparison: V2 adds a citation requirement to V1.

---

## 2. Evaluation Setup

- Golden set: `data/golden_set.jsonl`
- Number of questions: 20
- Candidate answers V1: `data/pairwise-v1-answers.json`
- Candidate answers V2: `data/pairwise-v2-answers.json`
- Judge model: `gpt-4o`
- Pairwise results: `data/pairwise-001-results.json`

Each pair was evaluated twice:

1. V1 presented as Candidate A and V2 as Candidate B.
2. V2 presented as Candidate A and V1 as Candidate B.

This position flip was used to detect position-sensitive judge decisions.

---

## 3. Aggregate Results

| Result | Count |
|---|---:|
| V1 wins | 2 |
| V2 wins | 0 |
| Ties | 10 |
| Ambiguous | 8 |
| Position-bias cases | 8 / 20 |
| Position-bias rate | 40.0% |

The position-bias rate of 40.0% is substantially higher than the healthy threshold specified for this experiment.

---

## 4. V1 Wins

### g006 — Teaching approaches

V1 was consistently preferred in both positions.

The judge found V1 more comprehensive because it provided specific teaching approaches, including differentiated instruction, active learning, formative assessment, collaborative learning, and technology integration.

When the candidate positions were reversed, the judge again preferred V1.

### g009 — Purpose of an education framework

V1 was also consistently preferred in both positions.

The judge considered V1 more comprehensive because it addressed curriculum alignment, assessment, instructional methods, educational goals, measuring outcomes, and lesson planning.

---

## 5. V2 Wins

There were no decisive V2 wins in this run.

This means the experiment did not produce evidence that the additional citation instruction in V2 consistently improved answer quality across the 20-question golden set.

---

## 6. Position-Bias Findings

Eight of the twenty comparisons were classified as ambiguous because the judge's decision changed after the candidate positions were reversed.

### g003 — Role of assessment

In the forward comparison, the judge preferred V2 because it appeared more comprehensive.

After reversing the candidate positions, the judge rated the two answers as a tie.

This indicates position-sensitive judging rather than a stable preference for V2.

### g015 — Connecting learning outcomes and assessment

In the forward comparison, the judge rated V1 and V2 as a tie.

After reversing the positions, the judge preferred V1.

Again, the decision changed after the position flip, so the result was classified as ambiguous.

These examples illustrate why the 40.0% position-bias rate needs to be taken seriously when interpreting the aggregate result.

---

## 7. Findings

1. V2 did not achieve any decisive wins over V1.
2. V1 achieved two consistent wins.
3. Half of the comparisons were ties (10/20).
4. Eight comparisons were affected by position-sensitive judging.
5. The 40.0% position-bias rate indicates that the pairwise judge was unstable for a substantial portion of this evaluation set.
6. The additional citation instruction in V2 therefore did not demonstrate a clear improvement in this experiment.

---

## 8. Decision

The result is **inconclusive rather than a definitive win for V1**.

Although V1 had two consistent wins and V2 had no decisive wins, the high 40.0% position-bias rate means the pairwise judge was not sufficiently stable to support a strong conclusion that V1 is objectively better.

For the next iteration, the position-bias issue should be investigated before treating this prompt comparison as strong evidence for a prompt decision.