"""
Week 5 — Evaluation Runner

Loads the golden set, gets candidate answers from the W4 /ask_batched API,
evaluates them using the LLM judge, and stores the results in eval_runs.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

import requests


# Add the Week5 project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.eval.judge import judge_one
from src.pipeline.store import ensure_schema

# ---------------------------------------------------------------------------
# 1. Command-line arguments
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the W5 LLM-as-Judge evaluation."
    )

    parser.add_argument(
        "--golden-set",
        required=True,
        help="Path to the golden-set JSONL file.",
    )

    parser.add_argument(
        "--db",
        required=True,
        help="Path to the SQLite database.",
    )

    parser.add_argument(
        "--api-url",
        required=True,
        help="Base URL of the W4 API.",
    )

    parser.add_argument(
        "--judge-model",
        default="gpt-4o",
        help="OpenAI model used as the judge.",
    )

    parser.add_argument(
        "--label",
        default="eval-run-001",
        help="Label for this evaluation run.",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# 2. Load golden set
# ---------------------------------------------------------------------------

def load_golden_set(path: str | Path) -> list[dict]:
    """Load one JSON object per line from the golden-set file."""

    entries = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            entries.append(json.loads(line))

    return entries


# ---------------------------------------------------------------------------
# 3. Call W4 /ask_batched
# ---------------------------------------------------------------------------

def get_candidate_answer(
    api_url: str,
    question: str,
) -> dict:
    """Send one question to the W4 /ask_batched endpoint."""

    url = api_url.rstrip("/") + "/ask_batched"

    response = requests.post(
        url,
        json={"question": question},
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


# ---------------------------------------------------------------------------
# 4. Save evaluation result
# ---------------------------------------------------------------------------

def save_eval_run(
    conn: sqlite3.Connection,
    *,
    golden_id: str,
    question: str,
    candidate_answer: str,
    ideal_answer: str,
    candidate_model: str,
    judge_model: str,
    accuracy: int,
    groundedness: int,
    format_score: int,
    reasoning: str,
    eval_run_label: str,
) -> None:
    """Insert one evaluation result into eval_runs."""

    conn.execute(
        """
        INSERT INTO eval_runs (
            golden_id,
            question,
            candidate_answer,
            ideal_answer,
            candidate_model,
            judge_model,
            accuracy,
            groundedness,
            format,
            reasoning,
            eval_run_label
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            golden_id,
            question,
            candidate_answer,
            ideal_answer,
            candidate_model,
            judge_model,
            accuracy,
            groundedness,
            format_score,
            reasoning,
            eval_run_label,
        ),
    )


# ---------------------------------------------------------------------------
# 5. Main evaluation loop
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    golden_entries = load_golden_set(args.golden_set)

    print("=" * 60)
    print("W5 LLM-as-Judge Evaluation")
    print("=" * 60)
    print(f"Golden set : {args.golden_set}")
    print(f"Database   : {args.db}")
    print(f"API        : {args.api_url}")
    print(f"Judge      : {args.judge_model}")
    print(f"Label      : {args.label}")
    print(f"Entries    : {len(golden_entries)}")
    print()

    # W4 Settings shows that the candidate model is gpt-4o-mini.
    candidate_model = "gpt-4o-mini"

    # Make sure the W5 database schema, including eval_runs, exists.
    ensure_schema(args.db)

    conn = sqlite3.connect(args.db)

    results = []
    started = time.time()

    try:
        for index, entry in enumerate(golden_entries, start=1):
            golden_id = entry["id"]
            question = entry["question"]
            ideal_answer = entry["ideal_answer"]

            print(
                f"[{index}/{len(golden_entries)}] "
                f"Evaluating {golden_id}: {question}"
            )

            # ---------------------------------------------------------------
            # Get candidate answer from W4.
            # ---------------------------------------------------------------

            answer = get_candidate_answer(
                args.api_url,
                question,
            )

            candidate_answer = answer["content"]

            # ---------------------------------------------------------------
            # Judge candidate against ideal answer.
            # ---------------------------------------------------------------

            score = judge_one(
                question=question,
                candidate_answer=candidate_answer,
                ideal_answer=ideal_answer,
                model=args.judge_model,
            )

            # ---------------------------------------------------------------
            # Save verdict.
            # ---------------------------------------------------------------

            save_eval_run(
                conn,
                golden_id=golden_id,
                question=question,
                candidate_answer=candidate_answer,
                ideal_answer=ideal_answer,
                candidate_model=candidate_model,
                judge_model=args.judge_model,
                accuracy=score.accuracy,
                groundedness=score.groundedness,
                format_score=score.format,
                reasoning=score.reasoning,
                eval_run_label=args.label,
            )

            conn.commit()

            results.append(score)

            print(
                f"    accuracy={score.accuracy} "
                f"groundedness={score.groundedness} "
                f"format={score.format}"
            )

    finally:
        conn.close()

    # -----------------------------------------------------------------------
    # 6. Aggregate results
    # -----------------------------------------------------------------------

    elapsed = time.time() - started

    if not results:
        print("No entries were scored.")
        return

    avg_accuracy = sum(r.accuracy for r in results) / len(results)
    avg_groundedness = (
        sum(r.groundedness for r in results) / len(results)
    )
    avg_format = sum(r.format for r in results) / len(results)

    accuracy_counts = {
        score: sum(r.accuracy == score for r in results)
        for score in range(4, 0, -1)
    }

    print()
    print("=" * 60)
    print(f"Aggregate for label='{args.label}'")
    print("-" * 60)
    print(f"n entries scored : {len(results)}")
    print(f"avg accuracy    : {avg_accuracy:.2f}")
    print(f"avg groundedness: {avg_groundedness:.2f}")
    print(f"avg format      : {avg_format:.2f}")
    print(
        "accuracy 4 / 3 / 2 / 1 : "
        f"{accuracy_counts[4]} / "
        f"{accuracy_counts[3]} / "
        f"{accuracy_counts[2]} / "
        f"{accuracy_counts[1]}"
    )
    print(f"wall-clock      : {elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()