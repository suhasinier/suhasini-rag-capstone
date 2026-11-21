
"""
Measure Week 8 Qdrant RAG latency and API cost.

Measures:
1. Query embedding
2. Qdrant retrieval
3. LLM answer generation
4. Total cost and latency per query

Uses the Week 8 collection: capstone_chunks_v2.
"""

import json
import statistics
import time
from pathlib import Path

from dotenv import load_dotenv

# --------------------------------------------------
# 1. Project paths and environment configuration
# --------------------------------------------------

WEEK8_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = WEEK8_DIR.parent

# Load the API keys and Qdrant credentials from Week8/.env
load_dotenv(WEEK8_DIR / ".env")

from openai import OpenAI

from src.rag.qdrant_rag import SYSTEM, CHAT_MODEL, EMBED_MODEL
from src.rag.qdrant_store import load_store


GOLDEN_FILE = (
    REPO_ROOT
    / "Week6"
    / "data"
    / "golden_set_cbse_class9_wk6_14-4-2.jsonl"
)

OUTPUT_FILE = WEEK8_DIR / "data" / "eval" / "qdrant_cost_latency.json"


# --------------------------------------------------
# 2. API pricing assumptions (USD per million tokens)
# --------------------------------------------------

EMBEDDING_PRICE_PER_MILLION = 0.02
LLM_INPUT_PRICE_PER_MILLION = 0.15
LLM_OUTPUT_PRICE_PER_MILLION = 0.60


# --------------------------------------------------
# 3. Calculate the 95th percentile
# --------------------------------------------------

def percentile(values, percent):
    """Calculate a percentile using linear interpolation."""

    return statistics.quantiles(
        values,
        n=100,
        method="inclusive"
    )[percent - 1]


# --------------------------------------------------
# 4. Main benchmark function
# --------------------------------------------------

def main():

    client = OpenAI()
    store = load_store()

    print("Week 8 Qdrant RAG cost and latency benchmark")
    print(f"Collection: {store.collection}")

    if store.collection != "capstone_chunks_v2":
        raise RuntimeError(
            "Incorrect collection. Expected capstone_chunks_v2."
        )

    with GOLDEN_FILE.open("r", encoding="utf-8") as file:
        questions = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    results = []

    # --------------------------------------------------
    # 5. Process every golden-set question
    # --------------------------------------------------

    for index, item in enumerate(questions, start=1):

        question = item["question"]
        start = time.perf_counter()

        # ----------------------------------------------
        # Stage 1: Embed the question
        # ----------------------------------------------

        stage_start = time.perf_counter()

        embedding_response = client.embeddings.create(
            model=EMBED_MODEL,
            input=[question],
        )

        query_vector = embedding_response.data[0].embedding
        embedding_tokens = embedding_response.usage.total_tokens

        embedding_ms = (
            time.perf_counter() - stage_start
        ) * 1000

        # ----------------------------------------------
        # Stage 2: Retrieve top 3 chunks from Qdrant
        # ----------------------------------------------

        stage_start = time.perf_counter()

        retrieved = store.client.query_points(
            collection_name=store.collection,
            query=query_vector,
            limit=3,
        ).points

        retrieval_ms = (
            time.perf_counter() - stage_start
        ) * 1000

        # ----------------------------------------------
        # Stage 3: Prepare context for the LLM
        # ----------------------------------------------

        context = "\n\n".join(
            f"[{hit.payload['chunk_id']}] "
            f"(source: {hit.payload.get('source', 'unknown')})\n"
            f"{hit.payload['text']}"
            for hit in retrieved
        )

        # ----------------------------------------------
        # Stage 4: Generate the answer
        # ----------------------------------------------

        stage_start = time.perf_counter()

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            temperature=0.0,
            messages=[
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": (
                        f"Context:\n{context}\n\n---\n\n"
                        f"Question: {question}"
                    ),
                },
            ],
        )

        generation_ms = (
            time.perf_counter() - stage_start
        ) * 1000

        answer = response.choices[0].message.content

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        # ----------------------------------------------
        # Stage 5: Calculate API cost
        # ----------------------------------------------

        embedding_cost = (
            embedding_tokens
            * EMBEDDING_PRICE_PER_MILLION
            / 1_000_000
        )

        input_cost = (
            input_tokens
            * LLM_INPUT_PRICE_PER_MILLION
            / 1_000_000
        )

        output_cost = (
            output_tokens
            * LLM_OUTPUT_PRICE_PER_MILLION
            / 1_000_000
        )

        total_cost = (
            embedding_cost + input_cost + output_cost
        )

        # ----------------------------------------------
        # Stage 6: Calculate total processing time
        # ----------------------------------------------

        total_ms = (
            time.perf_counter() - start
        ) * 1000

        # ----------------------------------------------
        # Stage 7: Save individual query results
        # ----------------------------------------------

        results.append({
            "question_id": item.get("id", f"q{index:02d}"),
            "question": question,
            "answer": answer,

            "sources": [
                hit.payload.get("source", "unknown")
                for hit in retrieved
            ],

            "chunk_ids": [
                hit.payload["chunk_id"]
                for hit in retrieved
            ],

            "embedding_tokens": embedding_tokens,
            "llm_input_tokens": input_tokens,
            "llm_output_tokens": output_tokens,

            "embedding_cost_usd": embedding_cost,
            "llm_input_cost_usd": input_cost,
            "llm_output_cost_usd": output_cost,
            "total_cost_usd": total_cost,

            "embedding_latency_ms": embedding_ms,
            "retrieval_latency_ms": retrieval_ms,
            "generation_latency_ms": generation_ms,
            "total_latency_ms": total_ms,
        })

        print(
            f"[{index}/{len(questions)}] "
            f"Latency: {total_ms:.0f} ms | "
            f"Cost: ${total_cost:.8f}"
        )

    # --------------------------------------------------
    # 8. Calculate overall benchmark metrics
    # --------------------------------------------------

    latencies = [
        result["total_latency_ms"]
        for result in results
    ]

    costs = [
        result["total_cost_usd"]
        for result in results
    ]

    summary = {
        "question_count": len(results),
        "embedding_model": EMBED_MODEL,
        "chat_model": CHAT_MODEL,
        "collection": store.collection,
        "top_k": 3,

        "latency_p50_ms": statistics.median(latencies),
        "latency_p95_ms": percentile(latencies, 95),

        "average_cost_per_query_usd": statistics.mean(costs),
        "total_cost_usd": sum(costs),

        "total_embedding_tokens": sum(
            result["embedding_tokens"]
            for result in results
        ),

        "total_llm_input_tokens": sum(
            result["llm_input_tokens"]
            for result in results
        ),

        "total_llm_output_tokens": sum(
            result["llm_output_tokens"]
            for result in results
        ),

        "pricing_assumptions_usd_per_million_tokens": {
            "text_embedding_3_small": EMBEDDING_PRICE_PER_MILLION,
            "gpt_4o_mini_input": LLM_INPUT_PRICE_PER_MILLION,
            "gpt_4o_mini_output": LLM_OUTPUT_PRICE_PER_MILLION,
        },

        "results": results,
    }

    # --------------------------------------------------
    # 9. Save benchmark results
    # --------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # 10. Display final summary
    # --------------------------------------------------

    print("\n=== Week 8 Cost and Latency Summary ===")

    print(f"Collection: {store.collection}")
    print(f"Questions measured: {len(results)}")

    print(
        f"Latency p50: "
        f"{summary['latency_p50_ms']:.2f} ms"
    )

    print(
        f"Latency p95: "
        f"{summary['latency_p95_ms']:.2f} ms"
    )

    print(
        "Average cost/query: "
        f"${summary['average_cost_per_query_usd']:.8f}"
    )

    print(
        f"Total benchmark cost: "
        f"${summary['total_cost_usd']:.8f}"
    )

    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
