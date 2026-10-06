"""
Week 5 — Generate candidate answers for a prompt variant.

Reads questions from the golden set and calls the Week 4 /ask_batched
endpoint. Saves the generated answers to a JSON file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate answers from the Week 4 API."
    )
    parser.add_argument(
        "--golden-set",
        required=True,
        help="Path to golden_set.jsonl",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL of the Week 4 API",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file",
    )
    return parser.parse_args()


def load_golden_set(path: str):
    entries = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                entries.append(json.loads(line))

    return entries


def main():
    args = parse_args()

    golden_entries = load_golden_set(args.golden_set)

    results = []

    print("=" * 60)
    print("Generating candidate answers")
    print("=" * 60)
    print(f"Questions : {len(golden_entries)}")
    print(f"API       : {args.api_url}")
    print(f"Output    : {args.output}")
    print()

    for index, entry in enumerate(golden_entries, start=1):
        golden_id = entry["id"]
        question = entry["question"]

        print(f"[{index}/{len(golden_entries)}] {golden_id}")

        response = requests.post(
            f"{args.api_url}/ask_batched",
            json={"question": question},
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        results.append(
            {
                "id": golden_id,
                "question": question,
                "answer": data["content"],
            }
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print(f"Saved {len(results)} answers to {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()