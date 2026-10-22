
import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Week6"))

from wk06_pipeline import retrieve

GOLDEN_FILE = (
    REPO_ROOT / "Week6/data/golden_set_cbse_class9_wk6_14-4-2.jsonl"
)

# Map each question to the PDF(s) expected to contain useful evidence.
SOURCE_MAP = {
    "g001": ["33_Circular_2026.pdf", "Curriculum_SecP1_2026-27.pdf"],
    "g002": ["33_Circular_2026.pdf", "Curriculum_SecP1_2026-27.pdf"],
    "g003": ["33_Circular_2026.pdf"],
    "g004": ["Curriculum_SecP1_2026-27.pdf"],
    "g005": ["Curriculum_SecP1_2026-27.pdf"],
    "g006": ["English_LL_SecP1IX_2026-27.pdf"],
    "g007": ["English_LL_SecP1IX_2026-27.pdf"],
    "g008": ["English_LL_SecP1IX_2026-27.pdf"],
    "g009": ["English_LL_SecP1IX_2026-27.pdf"],
    "g010": ["Maths_SecP1IX_2026-27.pdf"],
    "g011": ["Maths_SecP1IX_2026-27.pdf"],
    "g012": ["Maths_SecP1IX_2026-27.pdf"],
    "g013": ["Maths_SecP1IX_2026-27.pdf"],
    "g014": ["ScienceSt_SecP1_2026-27.pdf"],
    "g015": ["33_Circular_2026.pdf", "Curriculum_SecP1_2026-27.pdf"],
    "g016": ["ScienceSt_SecP1_2026-27.pdf"],
    "g017": ["Maths_SecP1IX_2026-27.pdf"],
    "g018": ["SocialScience_SecP1IX_2026-27.pdf"],
    "g019": [],
    "g020": [],
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--index", required=True)
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    index_path = Path(args.index)
    index = json.loads(index_path.read_text(encoding="utf-8"))

    with GOLDEN_FILE.open("r", encoding="utf-8") as file:
        questions = [json.loads(line) for line in file if line.strip()]

    records = []

    for item in questions:
        results = retrieve(item["question"], index, k=3)

        retrieved_sources = sorted({
            chunk["source_id"].rsplit("_p", 1)[0] + ".pdf"
            for chunk in results
            if chunk.get("source_id")
        })

        expected_sources = SOURCE_MAP.get(item["id"], [])
        is_out_of_corpus = item["id"] in {"g019", "g020"}

        # For in-corpus questions, check whether a relevant PDF appears.
        # For out-of-corpus questions, retrieval alone cannot prove abstention.
        hit = (
            any(source in retrieved_sources for source in expected_sources)
            if expected_sources
            else None
        )

        records.append({
            "id": item["id"],
            "question": item["question"],
            "expected_sources": expected_sources,
            "retrieved_sources": retrieved_sources,
            "hit": hit,
            "out_of_corpus": is_out_of_corpus,
            "ideal_answer": item["ideal_answer"],
        })

    output_dir = REPO_ROOT / "Week6/data/eval"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{args.label}.json"
    output_file.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    scored = [record for record in records if record["hit"] is not None]
    hits = sum(record["hit"] for record in scored)

    print(f"Label: {args.label}")
    print(f"Total questions: {len(records)}")
    print(f"In-corpus retrieval hit rate: {hits}/{len(scored)} = "
          f"{hits / len(scored):.2%}" if scored else "No scored questions")
    print("Out-of-corpus questions: 2 (require separate abstention testing)")
    print(f"Saved results to {output_file}")


if __name__ == "__main__":
    main()
