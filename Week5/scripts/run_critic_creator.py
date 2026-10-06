"""
Week 5 — Run Critic-Creator evaluation for one golden-set question.

Example:

python scripts/run_critic_creator.py \
    --golden-id g019 \
    --creator-model gpt-4o-mini \
    --judge-model gpt-4o \
    --max-rounds 3 \
    --threshold 3.5 \
    --output docs/critic-creator-trace.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make the Week5 project root importable when this script is
# executed from the repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.eval.critic_creator import critic_creator


def load_golden_entry(
    golden_path: Path,
    golden_id: str,
) -> dict:
    """Load one golden-set entry by ID."""

    with golden_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            entry = json.loads(line)

            if entry.get("id") == golden_id:
                return entry

    raise ValueError(
        f"Golden-set entry '{golden_id}' was not found in {golden_path}"
    )


def write_trace(
    output_path: Path,
    result: dict,
    golden_entry: dict,
) -> None:
    """Write the Critic-Creator run as a Markdown trace."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:

        f.write("# Critic-Creator Trace\n\n")

        f.write("## Run configuration\n\n")
        f.write(f"- Golden ID: `{golden_entry['id']}`\n")
        f.write(f"- Creator model: `{result['creator_model']}`\n")
        f.write(f"- Judge model: `{result['judge_model']}`\n")
        f.write(f"- Maximum rounds: `{result['max_rounds']}`\n")
        f.write(f"- Threshold: `{result['threshold']}`\n")
        f.write(
            f"- Converged: `{result['converged']}`\n"
        )

        if result["converged_round"] is not None:
            f.write(
                f"- Converged round: `{result['converged_round']}`\n"
            )

        f.write("\n")

        f.write("## Question\n\n")
        f.write(f"{golden_entry['question']}\n\n")

        f.write("## Ideal answer\n\n")
        f.write(f"{golden_entry['ideal_answer']}\n\n")

        f.write("## Round-by-round trace\n\n")

        for round_data in result["rounds"]:

            f.write(
                f"### Round {round_data['round']}\n\n"
            )

            f.write("**Creator answer:**\n\n")
            f.write(f"{round_data['answer']}\n\n")

            f.write("**Judge scores:**\n\n")
            f.write(
                f"- Accuracy: {round_data['accuracy']}\n"
            )
            f.write(
                f"- Groundedness: {round_data['groundedness']}\n"
            )
            f.write(
                f"- Format: {round_data['format']}\n"
            )
            f.write(
                f"- Mean: {round_data['mean']:.2f}\n\n"
            )

            f.write("**Judge reasoning:**\n\n")
            f.write(
                f"{round_data['reasoning']}\n\n"
            )

            if "critic_feedback" in round_data:
                f.write("**Critic feedback:**\n\n")
                f.write(
                    f"{round_data['critic_feedback']}\n\n"
                )

        f.write("## Final answer\n\n")
        f.write(f"{result['final_answer']}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Week 5 Critic-Creator loop."
    )

    parser.add_argument(
        "--golden-set",
        default="data/golden_set.jsonl",
        help="Path to the golden-set JSONL file.",
    )

    parser.add_argument(
        "--golden-id",
        required=True,
        help="Golden-set ID to evaluate, for example g019.",
    )

    parser.add_argument(
        "--creator-model",
        default="gpt-4o-mini",
        help="Model used by the Creator.",
    )

    parser.add_argument(
        "--judge-model",
        default="gpt-4o",
        help="Model used by the Judge and Critic.",
    )

    parser.add_argument(
        "--max-rounds",
        type=int,
        default=3,
        help="Maximum number of Creator rounds.",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=3.5,
        help="Mean score required for convergence.",
    )

    parser.add_argument(
        "--output",
        default="docs/critic-creator-trace.md",
        help="Markdown output path.",
    )

    args = parser.parse_args()

    golden_path = PROJECT_ROOT / args.golden_set
    output_path = PROJECT_ROOT / args.output

    golden_entry = load_golden_entry(
        golden_path,
        args.golden_id,
    )

    print(
        f"Running Critic-Creator for {golden_entry['id']}..."
    )

    result = critic_creator(
        question=golden_entry["question"],
        ideal_answer=golden_entry["ideal_answer"],
        creator_model=args.creator_model,
        judge_model=args.judge_model,
        max_rounds=args.max_rounds,
        threshold=args.threshold,
    )

    write_trace(
        output_path,
        result,
        golden_entry,
    )

    print("\nCritic-Creator complete.")
    print(f"Golden ID: {golden_entry['id']}")
    print(f"Converged: {result['converged']}")

    if result["converged_round"] is not None:
        print(
            f"Converged round: {result['converged_round']}"
        )

    print(
        f"Final answer: {result['final_answer']}"
    )
    print(
        f"Trace written to: {output_path}"
    )


if __name__ == "__main__":
    main()