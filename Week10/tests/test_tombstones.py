"""Tests for document tombstoning and live-record filtering."""

from types import SimpleNamespace

from qdrant_client.models import FieldCondition, IsEmptyCondition

from src.rag.pipeline import tombstone_source
from src.rag.retrieval import _live_filter


class FakeQdrantClient:
    """A small substitute for Qdrant used by these tests."""

    def __init__(self):
        self.count_arguments = None
        self.set_payload_arguments = None

    def count(self, **kwargs):
        self.count_arguments = kwargs
        return SimpleNamespace(count=3)

    def set_payload(self, **kwargs):
        self.set_payload_arguments = kwargs


class FakeStore:
    def __init__(self):
        self.client = FakeQdrantClient()
        self.collection = "test_collection"


def test_tombstone_source_marks_only_live_chunks_of_source():
    store = FakeStore()

    result = tombstone_source(store, "policy.pdf")

    assert result == 3

    count_args = store.client.count_arguments
    assert count_args["collection_name"] == "test_collection"
    assert count_args["exact"] is True

    conditions = count_args["count_filter"].must

    source_condition = next(
        condition
        for condition in conditions
        if isinstance(condition, FieldCondition)
    )
    assert source_condition.key == "source"
    assert source_condition.match.value == "policy.pdf"

    assert any(
        isinstance(condition, IsEmptyCondition)
        for condition in conditions
    )

    update_args = store.client.set_payload_arguments

    assert update_args["collection_name"] == "test_collection"
    assert "deleted_at" in update_args["payload"]
    assert update_args["points"] == count_args["count_filter"]
    assert update_args["wait"] is True


def test_live_filter_excludes_tombstoned_chunks():
    live_filter = _live_filter()

    assert any(
        isinstance(condition, IsEmptyCondition)
        for condition in live_filter.must
    )