import json
import sys
from pathlib import Path

from dotenv import load_dotenv

# Locate the Week6 project folder
WEEK6_ROOT = Path(__file__).resolve().parents[1]

# Load credentials from the Week6 .env file
load_dotenv(WEEK6_ROOT / ".env")

sys.path.insert(0, str(WEEK6_ROOT))

# Import OpenAI retrieval only after loading credentials
from wk06_pipeline import retrieve


# Files used for the comparison
GOLDEN_FILE = (
    WEEK6_ROOT / "data" / "golden_set_cbse_class9_wk6_14-4-2.jsonl"
)

OPENAI_INDEX_FILE = (
    WEEK6_ROOT / "data" / "embeddings_medium.json"
)

LOCAL_RESULTS_FILE = (
    WEEK6_ROOT / "data" / "eval" / "wk6-local-embeds.json"
)


def pdf_name(source_id):
    """Convert a page-level source ID into its PDF filename."""
    return source_id.rsplit("_p", 1)[0] + ".pdf"


def main():

    # Load the five questions: g001 to g005
    with GOLDEN_FILE.open("r", encoding="utf-8") as file:
        questions = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    selected_questions = [
        item for item in questions
        if item["id"] in {"g001", "g002", "g003", "g004", "g005"}
    ]

    # Load the OpenAI medium index
    openai_index = json.loads(
        OPENAI_INDEX_FILE.read_text(encoding="utf-8")
    )

    # Load the local evaluation results
    local_records = json.loads(
        LOCAL_RESULTS_FILE.read_text(encoding="utf-8")
    )

    local_by_id = {
        item["id"]: item
        for item in local_records
    }

    print("\nOPENAI vs LOCAL EMBEDDING COMPARISON")
    print("=" * 75)

    for item in selected_questions:

        question_id = item["id"]
        question = item["question"]

        # Retrieve top results using OpenAI embeddings
        openai_results = retrieve(
            question,
            openai_index,
            k=3
        )

        # Get the top result from the local evaluation
        local_record = local_by_id[question_id]
        local_top = local_record["top_results"][0]

        # Extract top source and cosine similarity
        openai_source = pdf_name(
            openai_results[0]["source_id"]
        )

        local_source = pdf_name(
            local_top["source_id"]
        )

        openai_score = openai_results[0]["score"]
        local_score = local_top["score"]

        same = openai_source == local_source

        print(f"\nQuestion: {question_id}")
        print(f"Text: {question}")
        print(f"OpenAI top source: {openai_source}")
        print(f"Local top source:  {local_source}")
        print(f"Same source?       {'Yes' if same else 'No'}")
        print(f"OpenAI cosine:     {openai_score:.4f}")
        print(f"Local cosine:      {local_score:.4f}")

    print("\nComparison completed.")


if __name__ == "__main__":
    main()
