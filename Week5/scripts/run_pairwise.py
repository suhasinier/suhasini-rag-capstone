"""
Week 5 — Pairwise Prompt Comparison Runner

This runner compares two sets of candidate answers.

Because the current W4 /ask_batched endpoint does not accept a
system_prompt field, candidate answers for v1 and v2 are supplied
through separate JSON files.

Expected answer-file format:
[
    {
        "id": "g001",
        "question": "...",
        "answer": "..."
    }
]

The script then:
1. Loads the golden set.
2. Loads v1 candidate answers.
3. Loads v2 candidate answers.
4. Runs the pairwise judge twice per question.
5. Flips the candidate positions on the second comparison.
6. Saves per-question results.
7. Prints the aggregate summary.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Add the Week5 project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.eval.pairwise import pairwise_compare


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the W5 pairwise prompt comparison."
    )

    parser.add_argument(
        "--golden-set",
        required=True,
        help="Path to the golden-set JSONL file.",
    )

    parser.add_argument(
        "--answers-v1",
        required=True,
        help="JSON file containing candidate answers generated with prompt v1.",
    )

    parser.add_argument(
        "--answers-v2",
        required=True,
        help="JSON file containing candidate answers generated with prompt v2.",
    )

    parser.add_argument(
        "--judge-model",
        default="gpt-4o",
        help="OpenAI model used as the pairwise judge.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the pairwise results JSON file.",
    )

    return parser.parse_args()


def load_golden_set(path: str | Path) -> list[dict]:
    entries = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            entries.append(json.loads(line))

    return entries


def load_answers(path: str | Path) -> dict[str, dict]:
    """
    Load candidate answers and index them by golden-set ID.
    """

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list.")

    indexed = {}

    for item in data:
        if "id" not in item or "answer" not in item:
            raise ValueError(
                f"Each answer entry in {path} must contain 'id' and 'answer'."
            )

        indexed[item["id"]] = item

    return indexed


def main():
    args = parse_args()

    golden_entries = load_golden_set(args.golden_set)
    answers_v1 = load_answers(args.answers_v1)
    answers_v2 = load_answers(args.answers_v2)

    print("=" * 60)
    print("W5 Pairwise Prompt Comparison")
    print("=" * 60)
    print(f"Golden set : {args.golden_set}")
    print(f"Answers v1 : {args.answers_v1}")
    print(f"Answers v2 : {args.answers_v2}")
    print(f"Judge      : {args.judge_model}")
    print(f"Entries    : {len(golden_entries)}")
    print()

    results = []
    started = time.time()

    for index, entry in enumerate(golden_entries, start=1):
        golden_id = entry["id"]
        question = entry["question"]

        if golden_id not in answers_v1:
            raise KeyError(
                f"{golden_id} is missing from {args.answers_v1}"
            )

        if golden_id not in answers_v2:
            raise KeyError(
                f"{golden_id} is missing from {args.answers_v2}"
            )

        answer_v1 = answers_v1[golden_id]["answer"]
        answer_v2 = answers_v2[golden_id]["answer"]

        print(
            f"[{index}/{len(golden_entries)}] "
            f"Comparing {golden_id}: {question}"
        )

        comparison = pairwise_compare(
            question=question,
            answer_a=answer_v1,
            answer_b=answer_v2,
            model=args.judge_model,
        )

        result = {
            "id": golden_id,
            "question": question,
            "winner": comparison["winner"],
            "position_bias": comparison["position_bias"],
            "forward": {
                "winner": comparison["forward"].winner,
                "reasoning": comparison["forward"].reasoning,
            },
            "reverse": {
                "winner": comparison["reverse"].winner,
                "reasoning": comparison["reverse"].reasoning,
            },
        }

        results.append(result)

        print(
            f"    winner={result['winner']} "
            f"position_bias={result['position_bias']}"
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    v1_wins = sum(r["winner"] == "A" for r in results)
    v2_wins = sum(r["winner"] == "B" for r in results)
    ties = sum(r["winner"] == "tie" for r in results)
    ambiguous = sum(r["winner"] == "ambiguous" for r in results)
    position_bias_count = sum(r["position_bias"] for r in results)

    elapsed = time.time() - started

    print()
    print("=" * 60)
    print("Pairwise summary")
    print("-" * 60)
    print(f"v1 wins          : {v1_wins}")
    print(f"v2 wins          : {v2_wins}")
    print(f"tie              : {ties}")
    print(f"ambiguous        : {ambiguous}")
    print(
        f"position-bias rate : "
        f"{position_bias_count}/{len(results)} = "
        f"{position_bias_count / len(results) * 100:.1f}%"
    )
    print(f"wall-clock       : {elapsed:.1f}s")
    print(f"results saved    : {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()