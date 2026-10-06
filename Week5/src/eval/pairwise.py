"""
Week 5 — Pairwise Prompt Comparison

Compares two candidate answers for the same question using an LLM judge.

The comparison is performed twice:
1. Candidate A is shown first, Candidate B second.
2. Candidate B is shown first, Candidate A second.

The second comparison flips the positions so that we can detect
position bias in the judge.
"""

from __future__ import annotations

import json

from openai import OpenAI
from pydantic import BaseModel, Field


class PairwiseResult(BaseModel):
    """Structured result returned by the pairwise judge."""

    winner: str = Field(pattern="^(A|B|tie)$")
    reasoning: str


PAIRWISE_RUBRIC = """You are an impartial evaluator comparing two candidate
answers to the same user question.

Judge the answers based on:
1. Accuracy — which answer better addresses the question and contains
   correct information?
2. Groundedness — which answer stays within the supplied context and
   avoids unsupported claims?
3. Completeness — which answer covers the important parts of the question?
4. Clarity and format — which answer is clearer, more direct, and better
   structured?

Do not choose a winner based on writing style alone. Prefer substantive
correctness and usefulness.

Candidate A and Candidate B may contain similar information. If they are
equally good, return "tie".

You must choose exactly one of:
- "A" — Candidate A is better
- "B" — Candidate B is better
- "tie" — neither candidate is meaningfully better

Give a concise explanation for your decision.

ALWAYS call the pairwise_compare tool. Never reply in plain text.
"""


PAIRWISE_TOOL = {
    "type": "function",
    "function": {
        "name": "pairwise_compare",
        "description": "Compare two candidate answers and select the better answer.",
        "parameters": {
            "type": "object",
            "properties": {
                "winner": {
                    "type": "string",
                    "enum": ["A", "B", "tie"],
                    "description": "Which candidate is better.",
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation supporting the decision.",
                },
            },
            "required": ["winner", "reasoning"],
            "additionalProperties": False,
        },
    },
}


def _compare_once(
    question: str,
    answer_a: str,
    answer_b: str,
    *,
    client: OpenAI,
    model: str,
) -> PairwiseResult:
    """Run one A-vs-B comparison."""

    user_prompt = f"""Question:
{question}

Candidate A:
{answer_a}

Candidate B:
{answer_b}

Compare Candidate A and Candidate B using the rubric.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PAIRWISE_RUBRIC},
            {"role": "user", "content": user_prompt},
        ],
        tools=[PAIRWISE_TOOL],
        tool_choice={
            "type": "function",
            "function": {"name": "pairwise_compare"},
        },
    )

    message = response.choices[0].message

    if not message.tool_calls:
        raise ValueError(
            "Pairwise judge did not return the required pairwise_compare tool call."
        )

    tool_call = message.tool_calls[0]

    if tool_call.function.name != "pairwise_compare":
        raise ValueError(
            f"Unexpected tool called: {tool_call.function.name}"
        )

    try:
        result = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Pairwise judge returned invalid JSON in the tool-call arguments."
        ) from exc

    return PairwiseResult.model_validate(result)


def pairwise_compare(
    question: str,
    answer_a: str,
    answer_b: str,
    *,
    client: OpenAI | None = None,
    model: str = "gpt-4o",
) -> dict:
    """
    Compare two answers twice with the positions flipped.

    Returns:
        {
            "forward": PairwiseResult,
            "reverse": PairwiseResult,
            "winner": "A" | "B" | "tie" | "ambiguous",
            "position_bias": bool
        }
    """

    if client is None:
        client = OpenAI()

    # First comparison:
    # A is shown first, B is shown second.
    forward = _compare_once(
        question,
        answer_a,
        answer_b,
        client=client,
        model=model,
    )

    # Second comparison:
    # B is shown first, A is shown second.
    reverse_position = _compare_once(
        question,
        answer_b,
        answer_a,
        client=client,
        model=model,
    )

    # Convert the reverse result back to the original A/B labels.
    if reverse_position.winner == "A":
        reverse_winner = "B"
    elif reverse_position.winner == "B":
        reverse_winner = "A"
    else:
        reverse_winner = "tie"

    # If the two judgments disagree, mark the result ambiguous.
    if forward.winner != reverse_winner:
        winner = "ambiguous"
        position_bias = True
    else:
        winner = forward.winner
        position_bias = False

    return {
        "forward": forward,
        "reverse": reverse_position,
        "winner": winner,
        "position_bias": position_bias,
    }