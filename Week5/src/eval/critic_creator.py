"""
Week 5 — Critic-Creator loop.

The Creator generates an answer.
The Judge scores the answer on:
    - accuracy
    - groundedness
    - format

If the mean score is below the convergence threshold,
the Critic provides feedback and the Creator revises the answer.

The loop runs for a maximum number of rounds.
"""

from __future__ import annotations

from openai import OpenAI

from .judge import JudgeScore, judge_one


CREATOR_SYSTEM_PROMPT = """You are an Enterprise Knowledge Assistant.

Answer the user's question accurately and clearly.

Rules:
1. Use the ideal answer as the target for correctness.
2. Do not invent facts.
3. Answer directly and clearly.
4. Keep the answer concise and useful.
5. When revising an answer, address the critic's valid feedback.
"""


CRITIC_SYSTEM_PROMPT = """You are a strict but constructive critic
evaluating an Enterprise Knowledge Assistant answer.

Review the candidate answer against the question and ideal answer.

Identify concrete problems that affect:
- accuracy
- groundedness
- format or clarity

Do not complain about harmless wording differences.
Focus on problems that should actually be fixed.

Return concise, actionable feedback for the Creator.
"""


def create_answer(
    question: str,
    ideal_answer: str,
    *,
    client: OpenAI | None = None,
    model: str = "gpt-4o-mini",
    previous_answer: str | None = None,
    critic_feedback: str | None = None,
) -> str:
    """Generate or revise an answer."""

    if client is None:
        client = OpenAI()

    user_content = f"""
Question:
{question}

Ideal answer:
{ideal_answer}
"""

    if previous_answer:
        user_content += f"""

Previous answer:
{previous_answer}

Critic feedback:
{critic_feedback or "No additional feedback."}

Revise the previous answer to address the critic's valid feedback.
Return only the improved answer.
"""

    else:
        user_content += """

Generate the best possible answer to the question.
Return only the answer.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CREATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )

    return response.choices[0].message.content or ""


def create_critic_feedback(
    question: str,
    ideal_answer: str,
    candidate_answer: str,
    *,
    client: OpenAI | None = None,
    model: str = "gpt-4o",
) -> str:
    """Generate actionable feedback for the next Creator round."""

    if client is None:
        client = OpenAI()

    user_content = f"""
Question:
{question}

Ideal answer:
{ideal_answer}

Candidate answer:
{candidate_answer}

Identify the most important concrete changes needed to improve
the candidate answer.

Return only actionable feedback for the Creator.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )

    return response.choices[0].message.content or ""


def critic_creator(
    question: str,
    ideal_answer: str,
    *,
    creator_model: str = "gpt-4o-mini",
    judge_model: str = "gpt-4o",
    max_rounds: int = 3,
    threshold: float = 3.5,
    client: OpenAI | None = None,
) -> dict:
    """
    Run the Critic-Creator improvement loop.

    Returns the complete round-by-round trace.
    """

    if client is None:
        client = OpenAI()

    rounds = []
    previous_answer = None
    critic_feedback = None

    for round_number in range(1, max_rounds + 1):

        # 1. Creator generates or revises the answer.
        answer = create_answer(
            question,
            ideal_answer,
            client=client,
            model=creator_model,
            previous_answer=previous_answer,
            critic_feedback=critic_feedback,
        )

        # 2. Judge scores the current answer.
        score: JudgeScore = judge_one(
            question=question,
            candidate_answer=answer,
            ideal_answer=ideal_answer,
            client=client,
            model=judge_model,
        )

        mean_score = (
            score.accuracy
            + score.groundedness
            + score.format
        ) / 3.0

        round_record = {
            "round": round_number,
            "answer": answer,
            "accuracy": score.accuracy,
            "groundedness": score.groundedness,
            "format": score.format,
            "mean": mean_score,
            "reasoning": score.reasoning,
        }

        rounds.append(round_record)

        # 3. Stop if the answer reaches the threshold.
        if mean_score >= threshold:
            return {
                "question": question,
                "creator_model": creator_model,
                "judge_model": judge_model,
                "max_rounds": max_rounds,
                "threshold": threshold,
                "converged": True,
                "converged_round": round_number,
                "rounds": rounds,
                "final_answer": answer,
            }

        # 4. No critic is needed after the final round.
        if round_number == max_rounds:
            break

        # 5. Critic identifies what should be improved.
        critic_feedback = create_critic_feedback(
            question,
            ideal_answer,
            answer,
            client=client,
            model=judge_model,
        )

        round_record["critic_feedback"] = critic_feedback

        # 6. Pass the current answer into the next Creator round.
        previous_answer = answer

    return {
        "question": question,
        "creator_model": creator_model,
        "judge_model": judge_model,
        "max_rounds": max_rounds,
        "threshold": threshold,
        "converged": False,
        "converged_round": None,
        "rounds": rounds,
        "final_answer": rounds[-1]["answer"] if rounds else "",
    }