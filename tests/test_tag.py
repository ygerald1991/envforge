"""Tests for envforge.tag module."""

import pytest

from envforge.tag import (
    add_tag,
    list_tags,
    remove_tag,
    snapshots_for_tag,
    tags_for_snapshot,
)


@pytest.fixture
def tag_dir(tmp_path):
    return str(tmp_path / "snapshots")


class TestAddTag:
    def test_adds_tag_to_index(self, tag_dir):
        add_tag("snap1", "production", tag_dir)
        result = list_tags(tag_dir)
        assert "production" in result
        assert "snap1" in result["production"]

    def test_multiple_snapshots_same_tag(self, tag_dir):
        add_tag("snap1", "staging", tag_dir)
        add_tag("snap2", "staging", tag_dir)
        result = snapshots_for_tag("staging", tag_dir)
        assert "snap1" in result
        assert "snap2" in result

    def test_duplicate_add_is_idempotent(self, tag_dir):
        add_tag("snap1", "dev", tag_dir)
        add_tag("snap1", "dev", tag_dir)
        result = snapshots_for_tag("dev", tag_dir)
        assert result.count("snap1") == 1

    def test_multiple_tags_on_same_snapshot(self, tag_dir):
        add_tag("snap1", "prod", tag_dir)
        add_tag("snap1", "release", tag_dir)
        tags = tags_for_snapshot("snap1", tag_dir)
        assert "prod" in tags
        assert "release" in tags


class TestRemoveTag:
    def test_removes_existing_tag(self, tag_dir):
        add_tag("snap1", "dev", tag_dir)
        result = remove_tag("snap1", "dev", tag_dir)
        assert result is True
        assert "snap1" not in snapshots_for_tag("dev", tag_dir)

    def test_removes_empty_tag_key(self, tag_dir):
        add_tag("snap1", "temp", tag_dir)
        remove_tag("snap1", "temp", tag_dir)
        assert "temp" not in list_tags(tag_dir)

    def test_returns_false_for_missing_tag(self, tag_dir):
        result = remove_tag("snap1", "nonexistent", tag_dir)
        assert result is False

    def test_returns_false_for_missing_snapshot_in_tag(self, tag_dir):
        add_tag("snap1", "dev", tag_dir)
        result = remove_tag("snap_other", "dev", tag_dir)
        assert result is False


class TestQueryFunctions:
    def test_snapshots_for_tag_empty(self, tag_dir):
        assert snapshots_for_tag("unknown", tag_dir) == []

    def test_tags_for_snapshot_empty(self, tag_dir):
        assert tags_for_snapshot("snap_none", tag_dir) == []

    def test_list_tags_empty_dir(self, tag_dir):
        assert list_tags(tag_dir) == {}

    def test_list_tags_returns_all(self, tag_dir):
        add_tag("s1", "alpha", tag_dir)
        add_tag("s2", "beta", tag_dir)
        tags = list_tags(tag_dir)
        assert set(tags.keys()) == {"alpha", "beta"}
