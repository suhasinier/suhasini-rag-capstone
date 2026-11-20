
import argparse
import json
import sys
from pathlib import Path

# Locate the Week6 project folder
REPO_ROOT = Path(__file__).resolve().parents[2]
WEEK6_ROOT = REPO_ROOT / "Week6"

sys.path.insert(0, str(WEEK6_ROOT))

# Import the local embedding function
from src.rag.embeddings_local import embed


GOLDEN_FILE = (
    WEEK6_ROOT / "data" / "golden_set_cbse_class9_wk6_14-4-2.jsonl"
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


def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""

    dot_product = sum(x * y for x, y in zip(a, b))

    magnitude_a = sum(x * x for x in a) ** 0.5
    magnitude_b = sum(y * y for y in b) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def retrieve_local(query, index, k=3):
    """Use local embeddings to retrieve the top-k matching chunks."""

    # Convert the question into a local embedding
    query_vector = embed(query)

    # Calculate similarity between the question and every chunk
    scored_chunks = []

    for chunk in index:
        score = cosine_similarity(query_vector, chunk["vector"])
        scored_chunks.append((score, chunk))

    # Sort by similarity, highest score first
    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    # Return the top-k chunks with their similarity scores
    return [
        {**chunk, "score": score}
        for score, chunk in scored_chunks[:k]
    ]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--label", required=True)
    parser.add_argument("--index", required=True)

    args = parser.parse_args()

    # Load the local embedding index
    index_path = Path(args.index)

    if not index_path.is_absolute():
        index_path = WEEK6_ROOT / index_path

    index = json.loads(index_path.read_text(encoding="utf-8"))

    # Load the same golden questions used by the OpenAI evaluation
    with GOLDEN_FILE.open("r", encoding="utf-8") as file:
        questions = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    records = []

    for item in questions:

        # Retrieve the top 3 chunks using local embeddings
        results = retrieve_local(item["question"], index, k=3)

        retrieved_sources = sorted({
            chunk["source_id"].rsplit("_p", 1)[0] + ".pdf"
            for chunk in results
            if chunk.get("source_id")
        })

        expected_sources = SOURCE_MAP.get(item["id"], [])
        is_out_of_corpus = item["id"] in {"g019", "g020"}

        # Check whether an expected PDF appears in the top 3 results
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

            # Retain the top chunks and scores for Step 5 comparison
            "top_results": [
                {
                    "source_id": chunk["source_id"],
                    "chunk_id": chunk["chunk_id"],
                    "score": chunk["score"],
                }
                for chunk in results
            ],
        })

    # Save results under the new evaluation label
    output_dir = WEEK6_ROOT / "data" / "eval"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{args.label}.json"

    output_file.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Calculate hit rate using only in-corpus questions
    scored = [
        record for record in records
        if record["hit"] is not None
    ]

    hits = sum(record["hit"] for record in scored)

    print(f"Label: {args.label}")
    print(f"Total questions: {len(records)}")

    if scored:
        print(
            f"In-corpus retrieval hit rate: "
            f"{hits}/{len(scored)} = {hits / len(scored):.2%}"
        )
    else:
        print("No scored questions")

    print("Out-of-corpus questions: 2 (require separate abstention testing)")
    print(f"Saved results to {output_file}")


if __name__ == "__main__":
    main()
