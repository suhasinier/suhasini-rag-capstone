
"""Evaluate Week 7 Qdrant retrieval using text-embedding-3-large."""

import json
from pathlib import Path

from src.rag.qdrant_rag import retrieve_large
from src.rag.qdrant_store import load_large_store

REPO_ROOT = Path(__file__).resolve().parents[2]

GOLDEN_FILE = (
    REPO_ROOT
    / "Week6/data/golden_set_cbse_class9_wk6_14-4-2.jsonl"
)

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
    questions = [
        json.loads(line)
        for line in GOLDEN_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    store = load_large_store()
    records = []

    for item in questions:
        results = retrieve_large(store, item["question"], k=3)

        retrieved_sources = sorted({
            result["source_id"].rsplit("_p", 1)[0] + ".pdf"
            for result in results
            if result.get("source_id")
        })

        expected_sources = SOURCE_MAP.get(item["id"], [])
        out_of_corpus = item["id"] in {"g019", "g020"}

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
            "out_of_corpus": out_of_corpus,
            "ideal_answer": item["ideal_answer"],
        })

    output_file = REPO_ROOT / "Week7/data/eval/qdrant_large.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    scored = [record for record in records if record["hit"] is not None]
    hits = sum(record["hit"] for record in scored)

    print("Week 7 Qdrant large-model retrieval evaluation")
    print(f"Total questions: {len(records)}")
    print(
        f"In-corpus retrieval hit rate: {hits}/{len(scored)} "
        f"= {hits / len(scored):.2%}"
        if scored
        else "No scored questions"
    )
    print("Out-of-corpus questions: 2 (abstention testing not measured here)")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
