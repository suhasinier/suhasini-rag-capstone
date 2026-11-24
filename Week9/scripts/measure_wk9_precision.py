
"""Measure W8 vs W9 precision@3 and precision@5.

Out-of-corpus questions are excluded from retrieval precision
and listed separately for abstention evaluation.
"""

import json
from pathlib import Path


from src.rag.retrieval import retrieve, dense_search
from src.rag.query_rewrite import step_back_retrieve

GOLDEN_SET = Path("data/golden_set.jsonl")

golden = [
    json.loads(line)
    for line in GOLDEN_SET.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

# Separate in-corpus and out-of-corpus questions.
in_corpus = [
    q for q in golden
    if q.get("expected_chunk_ids")
]

out_of_corpus = [
    q for q in golden
    if q.get("expected_abstention", False)
]

print(f"Total golden questions: {len(golden)}")
print(f"In-corpus questions: {len(in_corpus)}")
print(f"Out-of-corpus questions: {len(out_of_corpus)}")


def precision_at_k(retrieved_ids, expected_ids, k):
    """1.0 if at least one expected chunk appears in top-k."""
    return 1.0 if any(
        expected_id in retrieved_ids[:k]
        for expected_id in expected_ids
    ) else 0.0


def run_and_score(retriever_fn, label):
    p3_scores = []
    p5_scores = []
    per_question = []

    for q in in_corpus:
        hits = retriever_fn(q["question"], k=5)

        retrieved_ids = [
            hit["doc"].get("chunk_id")
            for hit in hits
        ]

        p3 = precision_at_k(
            retrieved_ids, q["expected_chunk_ids"], 3
        )
        p5 = precision_at_k(
            retrieved_ids, q["expected_chunk_ids"], 5
        )

        p3_scores.append(p3)
        p5_scores.append(p5)

        per_question.append({
            "id": q["id"],
            "question": q["question"],
            "p3": p3,
            "p5": p5,
        })

    return {
        "label": label,
        "p_at_3": sum(p3_scores) / len(p3_scores),
        "p_at_5": sum(p5_scores) / len(p5_scores),
        "per_question": per_question,
    }


# W8 baseline: pure dense retrieval.
baseline = run_and_score(
    lambda q, k: dense_search(q, k),
    "W8 dense-only"
)

# W9: hybrid retrieval + reranking.
w9 = run_and_score(
    retrieve,
    "W9 hybrid+rerank"
)
stretch = run_and_score(step_back_retrieve, "W9 + Step-back")

print("\n=== Precision comparison ===")
print(f"{'Metric':<12} {'W8 baseline':>14} {'W9':>14} {'Delta':>10}")

for metric in ("p_at_3", "p_at_5"):
    delta = w9[metric] - baseline[metric]
    print(
        f"{metric:<12} "
        f"{baseline[metric]:>14.3f} "
        f"{w9[metric]:>14.3f} "
        f"{delta:>+10.3f}"
    )

# Save per-question comparison.
output = Path("docs/wk9-precision-delta.md")

lines = [
    "# W9 Precision Delta — per-question breakdown",
    "",
    "| ID | Question | W8 P@3 | W9 P@3 | Change |",
    "|---|---|---:|---:|---|",
]

w8_by_id = {
    item["id"]: item for item in baseline["per_question"]
}
w9_by_id = {
    item["id"]: item for item in w9["per_question"]
}

for q in in_corpus:
    qid = q["id"]
    p8 = w8_by_id[qid]["p3"]
    p9 = w9_by_id[qid]["p3"]

    change = (
        "FIXED" if p9 > p8
        else "BROKE" if p9 < p8
        else "same"
    )

    lines.append(
        f"| {qid} | {q['question']} | {p8:.0f} | {p9:.0f} | {change} |"
    )

lines.extend([
    "",
    "## Out-of-corpus questions — separate abstention review",
    "",
    "| ID | Question | Expected behaviour |",
    "|---|---|---|",
])

for q in out_of_corpus:
    lines.append(
        f"| {q['id']} | {q['question']} | "
        "Abstain: information unavailable in corpus |"
    )

output.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"\nSaved per-question report to {output}")

print("\n=== Step-back comparison ===")
print(f"{'Metric':<10s} {'W9 Core':>12s} {'Step-back':>12s} {'Delta':>10s}")

for m in ["p_at_3", "p_at_5"]:
    delta = stretch[m] - w9[m]
    print(f"{m:<10s} {w9[m]:>12.3f} {stretch[m]:>12.3f} {delta:>+10.3f}")