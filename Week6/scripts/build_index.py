
import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Week6"))

from wk06_pipeline import chunk_documents, build_index

INPUT_FILE = REPO_ROOT / "Week6/data/parsed_cbse.jsonl"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--overlap", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Set your API key before building indexes."
        )

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"CBSE parsed data not found: {INPUT_FILE}")

    # Load the extracted CBSE page records.
    documents = []
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            documents.append({
                "id": record["source_id"],
                "text": record["text"],
            })

    print(f"CBSE page documents loaded: {len(documents)}")

    # Split CBSE text into chunks.
    chunks = chunk_documents(
        documents,
        size=args.size,
        overlap=args.overlap,
    )
    print(f"Chunks created: {len(chunks)}")

    # Generate embeddings for the chunks.
    index = build_index(chunks)

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(index, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"CBSE index saved: {output_path}")


if __name__ == "__main__":
    main()
