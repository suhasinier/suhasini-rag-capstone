
"""Evaluate local MiniLM retrieval using the Week 6 CBSE golden set."""

import json
import time
import statistics
from pathlib import Path

from dotenv import load_dotenv

from src.rag.qdrant_local_rag import retrieve_local
from src.rag.qdrant_store import QdrantStore, load_store

# Load Qdrant credentials from the repository root.
REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

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

LOCAL_COLLECTION = "capstone_chunks_local"


def main():
    # Read the golden-set questions.
    questions = [
        json.loads(line)
        for line in GOLDEN_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    # Connect to the local-embedding collection.
    existing_store = load_store()

    store = QdrantStore(
        client=existing_store.client,
        collection=LOCAL_COLLECTION,
    )

    records = []
    latencies = []

    print("Evaluating local MiniLM retrieval...")

    for item in questions:
        start = time.perf_counter()

        results = retrieve_local(store, item["question"], k=3)

        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

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
            "latency_ms": round(elapsed_ms, 2),
            "ideal_answer": item["ideal_answer"],
        })

        print(
            f"{item['id']}: "
            f"{'HIT' if hit else 'MISS' if hit is not None else 'OUT-OF-CORPUS'} "
            f"({elapsed_ms:.2f} ms)"
        )

    # Save individual question results.
    output_file = REPO_ROOT / "Week7/data/eval/qdrant_local.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_file.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Calculate retrieval hit rate.
    scored = [record for record in records if record["hit"] is not None]
    hits = sum(record["hit"] for record in scored)

    hit_rate = hits / len(scored) if scored else 0

    # Calculate median retrieval latency.
    p50_latency = statistics.median(latencies) if latencies else 0

    print("\nLocal MiniLM retrieval evaluation")
    print(f"Total questions: {len(records)}")
    print(
        f"In-corpus retrieval hit rate: {hits}/{len(scored)} "
        f"= {hit_rate:.2%}"
    )
    print("Out-of-corpus questions: 2")
    print(f"Median retrieval latency (p50): {p50_latency:.2f} ms")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
