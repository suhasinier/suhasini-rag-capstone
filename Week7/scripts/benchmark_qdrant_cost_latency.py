"""Measure Qdrant RAG latency and API cost for the Week 7 CBSE evaluation set."""

import json
import statistics
import time
from pathlib import Path

from openai import OpenAI

from src.rag.qdrant_rag import SYSTEM, CHAT_MODEL, EMBED_MODEL
from src.rag.qdrant_store import load_store


# Run from the Week7 directory.
EVAL_FILE = Path("../Week6/data/golden_set_cbse_class9_wk6_14-4-2.jsonl")
OUTPUT_FILE = Path("data/eval/qdrant_cost_latency.json")

# Standard API rates in USD per 1 million tokens.
EMBEDDING_PRICE_PER_MILLION = 0.02
LLM_INPUT_PRICE_PER_MILLION = 0.15
LLM_OUTPUT_PRICE_PER_MILLION = 0.60


def percentile(values, percent):
    """Calculate a percentile using linear interpolation."""
    return statistics.quantiles(
        values, n=100, method="inclusive"
    )[percent - 1]


def main():
    client = OpenAI()
    store = load_store()

    with EVAL_FILE.open("r", encoding="utf-8") as file:
        questions = [json.loads(line) for line in file if line.strip()]

    results = []

    for index, item in enumerate(questions, start=1):
        question = item["question"]
        start = time.perf_counter()

        # 1. Embed the question and record actual embedding token usage.
        stage_start = time.perf_counter()
        embedding_response = client.embeddings.create(
            model=EMBED_MODEL,
            input=[question],
        )
        query_vector = embedding_response.data[0].embedding
        embedding_tokens = embedding_response.usage.total_tokens
        embedding_ms = (time.perf_counter() - stage_start) * 1000

        # 2. Retrieve the top 3 chunks from Qdrant.
        stage_start = time.perf_counter()
        retrieved = store.client.query_points(
            collection_name=store.collection,
            query=query_vector,
            limit=3,
        ).points
        retrieval_ms = (time.perf_counter() - stage_start) * 1000

        context = "\n\n".join(
            f"[{hit.payload['chunk_id']}] "
            f"(source: {hit.payload['source_id']})\n"
            f"{hit.payload['text']}"
            for hit in retrieved
        )

        # 3. Generate an answer using the existing RAG system prompt.
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
        generation_ms = (time.perf_counter() - stage_start) * 1000

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        embedding_cost = (
            embedding_tokens * EMBEDDING_PRICE_PER_MILLION / 1_000_000
        )
        input_cost = (
            input_tokens * LLM_INPUT_PRICE_PER_MILLION / 1_000_000
        )
        output_cost = (
            output_tokens * LLM_OUTPUT_PRICE_PER_MILLION / 1_000_000
        )
        total_cost = embedding_cost + input_cost + output_cost

        total_ms = (time.perf_counter() - start) * 1000

        results.append(
            {
                "question_id": item.get("id", f"q{index:02d}"),
                "question": question,
                "answer": response.choices[0].message.content,
                "sources": [
                    hit.payload["source_id"] for hit in retrieved
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
            }
        )

        print(
            f"[{index}/{len(questions)}] "
            f"Latency: {total_ms:.0f} ms | "
            f"Cost: ${total_cost:.8f}"
        )

    latencies = [r["total_latency_ms"] for r in results]
    costs = [r["total_cost_usd"] for r in results]

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
            r["embedding_tokens"] for r in results
        ),
        "total_llm_input_tokens": sum(
            r["llm_input_tokens"] for r in results
        ),
        "total_llm_output_tokens": sum(
            r["llm_output_tokens"] for r in results
        ),
        "pricing_assumptions_usd_per_million_tokens": {
            "text_embedding_3_small": EMBEDDING_PRICE_PER_MILLION,
            "gpt_4o_mini_input": LLM_INPUT_PRICE_PER_MILLION,
            "gpt_4o_mini_output": LLM_OUTPUT_PRICE_PER_MILLION,
        },
        "results": results,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n=== Week 7 Cost and Latency Summary ===")
    print(f"Questions measured: {len(results)}")
    print(f"Latency p50: {summary['latency_p50_ms']:.2f} ms")
    print(f"Latency p95: {summary['latency_p95_ms']:.2f} ms")
    print(
        "Average cost/query: "
        f"${summary['average_cost_per_query_usd']:.8f}"
    )
    print(f"Total benchmark cost: ${summary['total_cost_usd']:.8f}")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()