"""Tests for the Week 10 semantic cache."""

import pytest

from src.rag import cache


def test_lookup_returns_none_for_empty_cache(tmp_path):
    db_path = str(tmp_path / "test_cache.db")

    result = cache.lookup(
        [1.0, 0.0],
        db_path=db_path,
    )

    assert result is None


def test_put_and_lookup_returns_cached_answer(tmp_path):
    db_path = str(tmp_path / "test_cache.db")

    cache.put(
        question="What is photosynthesis?",
        embedding=[1.0, 0.0],
        answer="Photosynthesis is the process by which plants make food.",
        db_path=db_path,
    )

    result = cache.lookup(
        [1.0, 0.0],
        db_path=db_path,
    )

    assert result is not None
    assert result["answer"] == (
        "Photosynthesis is the process by which plants make food."
    )
    assert result["matched_question"] == "What is photosynthesis?"
    assert result["similarity"] == pytest.approx(1.0)


def test_lookup_rejects_question_below_similarity_threshold(tmp_path):
    db_path = str(tmp_path / "test_cache.db")

    cache.put(
        question="What is photosynthesis?",
        embedding=[1.0, 0.0],
        answer="Plants make food through photosynthesis.",
        db_path=db_path,
    )

    result = cache.lookup(
        [0.0, 1.0],
        threshold=0.95,
        db_path=db_path,
    )

    assert result is None


def test_stats_and_clear(tmp_path):
    db_path = str(tmp_path / "test_cache.db")

    cache.put("Question one", [1.0, 0.0], "Answer one", db_path=db_path)
    cache.put("Question two", [0.0, 1.0], "Answer two", db_path=db_path)

    before_lookup = cache.stats(db_path=db_path)

    assert before_lookup["n_entries"] == 2
    assert before_lookup["total_hits"] == 0

    cache.lookup([1.0, 0.0], db_path=db_path)

    after_lookup = cache.stats(db_path=db_path)

    assert after_lookup["n_entries"] == 2
    assert after_lookup["total_hits"] == 1

    deleted_count = cache.clear(db_path=db_path)

    assert deleted_count == 2

    after_clear = cache.stats(db_path=db_path)

    assert after_clear["n_entries"] == 0
    assert after_clear["total_hits"] == 0