from types import SimpleNamespace

import pytest

from src.eval.judge import JudgeScore, RUBRIC_PROMPT, judge_one


def make_tool_response(arguments, tool_name="rate_answer"):
    """Create a fake OpenAI response containing a tool call."""
    tool_call = SimpleNamespace(
        function=SimpleNamespace(
            name=tool_name,
            arguments=arguments,
        )
    )

    message = SimpleNamespace(
        tool_calls=[tool_call]
    )

    choice = SimpleNamespace(
        message=message
    )

    return SimpleNamespace(
        choices=[choice]
    )


class FakeCompletions:
    def __init__(self, response):
        self.response = response
        self.called_with = None

    def create(self, **kwargs):
        self.called_with = kwargs
        return self.response


class FakeClient:
    def __init__(self, response):
        self.chat = SimpleNamespace(
            completions=FakeCompletions(response)
        )


def test_rubric_prompt_is_long_enough():
    words = len(RUBRIC_PROMPT.split())
    assert words > 100


def test_judge_score_accepts_valid_scores():
    score = JudgeScore(
        accuracy=4,
        groundedness=3,
        format=4,
        reasoning="The answer is mostly correct and well supported.",
    )

    assert score.accuracy == 4
    assert score.groundedness == 3
    assert score.format == 4


@pytest.mark.parametrize(
    "field",
    ["accuracy", "groundedness", "format"],
)
def test_judge_score_rejects_scores_outside_range(field):
    values = {
        "accuracy": 4,
        "groundedness": 4,
        "format": 4,
        "reasoning": "Test reasoning",
    }

    values[field] = 5

    with pytest.raises(Exception):
        JudgeScore(**values)


def test_judge_one_parses_valid_tool_call():
    arguments = (
        '{"accuracy": 4, '
        '"groundedness": 3, '
        '"format": 4, '
        '"reasoning": "Good answer."}'
    )

    response = make_tool_response(arguments)
    client = FakeClient(response)

    result = judge_one(
        question="What is RAG?",
        candidate_answer="RAG retrieves relevant information before generation.",
        ideal_answer="RAG combines retrieval with generation.",
        client=client,
    )

    assert isinstance(result, JudgeScore)
    assert result.accuracy == 4
    assert result.groundedness == 3
    assert result.format == 4


def test_judge_one_requires_tool_call():
    message = SimpleNamespace(tool_calls=[])
    choice = SimpleNamespace(message=message)
    response = SimpleNamespace(choices=[choice])

    client = FakeClient(response)

    with pytest.raises(ValueError, match="required rate_answer tool call"):
        judge_one(
            question="What is RAG?",
            candidate_answer="An answer.",
            ideal_answer="The ideal answer.",
            client=client,
        )


def test_judge_one_rejects_wrong_tool():
    response = make_tool_response(
        '{"accuracy": 4, "groundedness": 4, "format": 4, '
        '"reasoning": "Good."}',
        tool_name="wrong_tool",
    )

    client = FakeClient(response)

    with pytest.raises(ValueError, match="Unexpected tool called"):
        judge_one(
            question="What is RAG?",
            candidate_answer="An answer.",
            ideal_answer="The ideal answer.",
            client=client,
        )


def test_judge_one_rejects_invalid_json():
    response = make_tool_response(
        '{"accuracy": 4, "groundedness": 4, '
        '"format": 4, "reasoning": "broken"'
    )

    client = FakeClient(response)

    with pytest.raises(ValueError, match="invalid JSON"):
        judge_one(
            question="What is RAG?",
            candidate_answer="An answer.",
            ideal_answer="The ideal answer.",
            client=client,
        )


def test_judge_one_rejects_invalid_score():
    response = make_tool_response(
        '{"accuracy": 5, '
        '"groundedness": 4, '
        '"format": 4, '
        '"reasoning": "Invalid accuracy score."}'
    )

    client = FakeClient(response)

    with pytest.raises(Exception):
        judge_one(
            question="What is RAG?",
            candidate_answer="An answer.",
            ideal_answer="The ideal answer.",
            client=client,
        )