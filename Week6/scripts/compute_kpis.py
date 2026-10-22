
import argparse
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
EVAL_DIR = BASE_DIR / "data" / "eval"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metric",
        required=True,
        choices=["retrieval_hit_rate", "cost_per_query"],
    )
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    result_file = EVAL_DIR / f"{args.label}.json"
    records = json.loads(result_file.read_text(encoding="utf-8"))

    if args.metric == "retrieval_hit_rate":
        if not records:
            print("No evaluation records found.")
            return

        hits = sum(bool(record.get("hit", False)) for record in records)
        rate = hits / len(records)
        print(f"Label: {args.label}")
        print(f"Retrieval hit rate: {hits}/{len(records)} = {rate:.2%}")

    else:
        print(
            "Cost per query is unavailable: the evaluation records "
            "do not contain API token usage or cost."
        )


if __name__ == "__main__":
    main()
