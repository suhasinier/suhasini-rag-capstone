"""
Week 5 — LLM-as-a-Judge

Scores a candidate answer against an ideal answer using three dimensions:

1. Accuracy
2. Groundedness
3. Format

The judge returns a structured JudgeScore using OpenAI tool calling.
"""

import json
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. Structured result returned by the judge
# ---------------------------------------------------------------------------

class JudgeScore(BaseModel):
    """Structured evaluation produced by the LLM judge."""

    accuracy: int = Field(ge=1, le=4)
    groundedness: int = Field(ge=1, le=4)
    format: int = Field(ge=1, le=4)
    reasoning: str


# ---------------------------------------------------------------------------
# 2. Rubric used by the judge
# ---------------------------------------------------------------------------

RUBRIC_PROMPT = """
You are a senior evaluator for an AI-powered CBSE/NCERT education and
curriculum assistant. Evaluate a candidate answer against the user's
question and the provided ideal answer. Score the candidate independently
on Accuracy, Groundedness, and Format using a 1–4 scale.

ACCURACY:
1 = The answer is substantially incorrect, misses the main question, or
contains major factual errors.
2 = The answer contains some correct information but has important
omissions, inaccuracies, or misleading statements.
3 = The answer is mostly correct and addresses the main question, with only
minor omissions or imprecision.
4 = The answer is fully correct, directly answers the question, and contains
no important factual errors when compared with the ideal answer.

GROUNDEDNESS:
1 = The answer makes unsupported claims, invents information, or presents
uncertainty as fact.
2 = Some claims are reasonable, but important statements are insufficiently
supported or go beyond the information represented by the ideal answer.
3 = Most claims are supported by the information represented in the ideal
answer, with only minor unsupported or overly broad statements.
4 = The answer stays closely grounded in the information represented by the
ideal answer, avoids invented claims, and appropriately acknowledges
uncertainty or limitations when necessary.

FORMAT:
1 = The answer is difficult to use, poorly structured, incomplete, or does
not follow the expected answer style.
2 = The answer is understandable but has noticeable problems with clarity,
organization, length, or required information.
3 = The answer is clear, relevant, reasonably concise, and well organized,
with only minor presentation issues.
4 = The answer is clear, concise, directly relevant, well organized, and
appropriate for a teacher asking a curriculum-related question. It includes
important details without unnecessary information.

Judge the candidate against the question and ideal answer, not against
personal preferences. Do not reward an answer simply because it is fluent.
Correctness and evidence are more important than style.

Provide a brief reasoning statement that explains the important evidence
behind the three scores.

ALWAYS call the rate_answer tool. Never reply in plain text.
"""


# ---------------------------------------------------------------------------
# 3. Tool definition
# ---------------------------------------------------------------------------

RATE_ANSWER_TOOL = {
    "type": "function",
    "function": {
        "name": "rate_answer",
        "description": (
            "Evaluate a candidate answer against an ideal answer "
            "using accuracy, groundedness, and format scores."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "accuracy": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 4,
                    "description": "Accuracy score from 1 to 4.",
                },
                "groundedness": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 4,
                    "description": "Groundedness score from 1 to 4.",
                },
                "format": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 4,
                    "description": "Format score from 1 to 4.",
                },
                "reasoning": {
                    "type": "string",
                    "description": (
                        "Brief explanation supporting the three scores."
                    ),
                },
            },
            "required": [
                "accuracy",
                "groundedness",
                "format",
                "reasoning",
            ],
            "additionalProperties": False,
        },
    },
}


# ---------------------------------------------------------------------------
# 4. Judge one answer
# ---------------------------------------------------------------------------

def judge_one(
    question: str,
    candidate_answer: str,
    ideal_answer: str,
    *,
    client: Optional[OpenAI] = None,
    model: str = "gpt-4o",
) -> JudgeScore:
    """
    Evaluate one candidate answer against its ideal answer.

    Parameters
    ----------
    question:
        The original user question.

    candidate_answer:
        The answer produced by the system being evaluated.

    ideal_answer:
        The expected high-quality answer from the golden set.

    client:
        Optional OpenAI client. If omitted, a new client is created.

    model:
        Judge model to use. Defaults to gpt-4o.
    """

    if client is None:
        client = OpenAI()

    user_prompt = f"""
Question:
{question}

Ideal answer:
{ideal_answer}

Candidate answer:
{candidate_answer}

Evaluate the candidate answer using the rubric.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": RUBRIC_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        tools=[RATE_ANSWER_TOOL],
        tool_choice={
            "type": "function",
            "function": {
                "name": "rate_answer",
            },
        },
    )

    # -----------------------------------------------------------------------
    # 5. Extract the tool call
    # -----------------------------------------------------------------------

    message = response.choices[0].message

    if not message.tool_calls:
        raise ValueError(
            "Judge model did not return the required rate_answer tool call."
        )

    tool_call = message.tool_calls[0]

    if tool_call.function.name != "rate_answer":
        raise ValueError(
            f"Unexpected tool called: {tool_call.function.name}"
        )

    # -----------------------------------------------------------------------
    # 6. Parse JSON returned by the tool call
    # -----------------------------------------------------------------------

    try:
        result = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Judge returned invalid JSON in the tool-call arguments."
        ) from exc

    # -----------------------------------------------------------------------
    # 7. Validate and construct JudgeScore
    # -----------------------------------------------------------------------

    return JudgeScore.model_validate(result)