"""Async batch pipeline — STARTER file for Week 2.

You will complete this file across sub-steps 2b → 2e. Each stub maps to one
sub-step:
  - ask_llm                — 2b
  - ask_llm_with_retry      — 2c
  - run_batch               — 2d
  - JSON-logging block      — 2e

After Step 2a, you renamed this file to `src/pipeline/pipeline.py` and changed
the `from fake_llm import ...` import below to `from .fake_llm import ...`.

The completed reference is at <cohort-repo>/week2/reference/pipeline_reference.py.
"""
from __future__ import annotations
import asyncio
import json
import logging
import sys
import time

import csv
from pathlib import Path

from .settings import Settings, RunSummary

_settings_for_import = Settings()

if _settings_for_import.use_fake:
    from .fake_llm import Question, Answer, fake_ask_llm, FakeLLMError
else:
    from dotenv import load_dotenv
    from openai import AsyncOpenAI
    from pydantic import BaseModel

    load_dotenv()
    _client = AsyncOpenAI()

    class Question(BaseModel):
        text: str

    class Answer(BaseModel):
        question: str
        text: str
        cost_usd: float
        retries: int = 0

from .logging_config import get_logger
from .settings import Settings, RunSummary

log = get_logger()

def load_questions(path: str | Path = "data/questions.csv") -> list[Question]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    return [Question(text=row["text"]) for row in rows if row.get("text")]


def summarise_run(
    answers: list[Answer],
    *,
    started_at: float,
    elapsed: float,
    fail_rate: float,
    use_fake: bool,
) -> RunSummary:
    return RunSummary(
        started_at=started_at,
        elapsed_seconds=elapsed,
        n_questions=len(answers),
        n_succeeded=len(answers),
        n_retries_total=sum(a.retries for a in answers),
        total_cost_usd=sum(a.cost_usd for a in answers),
        fail_rate=fail_rate,
        use_fake=use_fake,
    )
# ─────────────────────────────────────────────────────────────────────────────
# Step 5 (sub-step 2e) — structured (JSON) logging
#
# 2e: Replace this commented block with:
#   - A `JsonFormatter(logging.Formatter)` class whose `format(record)` returns
#     `json.dumps({"ts": ..., "level": ..., "msg": ...})`
#   - A module-level `log = logging.getLogger("pipeline")` + setLevel(INFO)
#   - A StreamHandler attached to that logger, using JsonFormatter()
# ─────────────────────────────────────────────────────────────────────────────



# ─────────────────────────────────────────────────────────────────────────────
# 2b — single LLM call
# ─────────────────────────────────────────────────────────────────────────────
async def ask_llm(q: Question, fail_rate: float = 0.0) -> Answer:
    if _settings_for_import.use_fake:
        ans = await fake_ask_llm(q, fail_rate=fail_rate)
    else:
        resp = await _client.chat.completions.create(
            model=_settings_for_import.model,
            messages=[{"role": "user", "content": q.text}],
        )

        ans = Answer(
            question=q.text,
            text=resp.choices[0].message.content,
            cost_usd=0.0001,
        )

    log.info(f"asked: {q.text[:40]}")
    return ans


# ─────────────────────────────────────────────────────────────────────────────
# 2c — retry wrapper
# ─────────────────────────────────────────────────────────────────────────────
async def ask_llm_with_retry(
    q: Question, tries: int = 3, fail_rate: float = 0.0
) -> Answer:
    """Retry up to `tries` times. Wait 1 s, 2 s, 4 s between attempts."""
    for attempt in range(tries):
        try:
            ans = await ask_llm(q, fail_rate=fail_rate)
            ans.retries = attempt
            return ans
        except Exception as exc:
            if attempt == tries - 1:
                raise
            log.warning(f"retry {attempt + 1} for: {q.text[:40]} ({exc})")
            await asyncio.sleep(2 ** attempt)

    raise RuntimeError("unreachable")


# ─────────────────────────────────────────────────────────────────────────────
# 2d — batch runner
# ─────────────────────────────────────────────────────────────────────────────
async def run_batch(
    questions: list[Question], fail_rate: float = 0.0
) -> list[Answer]:
    """Fire every question in parallel via asyncio.gather (with retries)."""
    tasks = [ask_llm_with_retry(q, fail_rate=fail_rate) for q in questions]
    return await asyncio.gather(*tasks)

async def run_in_batches(
    questions: list[Question], batch_size: int = 5, fail_rate: float = 0.0
) -> list[Answer]:
    out: list[Answer] = []

    for i in range(0, len(questions), batch_size):
        chunk = questions[i : i + batch_size]

        log.info(f"batch {i // batch_size + 1}: {len(chunk)} questions")

        batch_answers = await asyncio.gather(
            *(ask_llm_with_retry(q, fail_rate=fail_rate) for q in chunk)
        )

        out.extend(batch_answers)

        await asyncio.sleep(0.1)

    return out
# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint — replaced in Step 3a (Settings) and again in Step 3c (CSV + batched)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    settings = Settings()

    questions = load_questions(settings.questions_csv)
    log.info(f"loaded {len(questions)} questions")

    started = time.time()

    answers = asyncio.run(
        run_in_batches(
            questions,
            batch_size=settings.batch_size,
            fail_rate=settings.fail_rate,
        )
    )

    elapsed = time.time() - started

    summary = summarise_run(
        answers,
        started_at=started,
        elapsed=elapsed,
        fail_rate=settings.fail_rate,
        use_fake=settings.use_fake,
    )

    log.info(f"summary: {summary.model_dump_json()}")

    settings.results_json.write_text(
        json.dumps(
            {
                "summary": summary.model_dump(mode="json"),
                "answers": [a.model_dump() for a in answers],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"wrote {len(answers)} answers to "
        f"{settings.results_json} in {elapsed:.2f}s"
    )
