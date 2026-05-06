"""Tests for envforge.snapshot_comment."""

import pytest
from pathlib import Path
from envforge.snapshot_comment import (
    add_comment,
    get_comments,
    delete_comment,
    clear_comments,
    format_comments,
)


@pytest.fixture
def cdir(tmp_path):
    return str(tmp_path)


def test_add_comment_returns_entry(cdir):
    entry = add_comment(cdir, "snap1", "alice", "looks good")
    assert entry["author"] == "alice"
    assert entry["text"] == "looks good"
    assert "timestamp" in entry


def test_add_comment_persists(cdir):
    add_comment(cdir, "snap1", "bob", "needs review")
    comments = get_comments(cdir, "snap1")
    assert len(comments) == 1
    assert comments[0]["author"] == "bob"


def test_get_comments_missing_snapshot_returns_empty(cdir):
    result = get_comments(cdir, "nonexistent")
    assert result == []


def test_multiple_comments_ordered(cdir):
    add_comment(cdir, "snap1", "alice", "first")
    add_comment(cdir, "snap1", "bob", "second")
    comments = get_comments(cdir, "snap1")
    assert len(comments) == 2
    assert comments[0]["text"] == "first"
    assert comments[1]["text"] == "second"


def test_delete_comment_removes_entry(cdir):
    add_comment(cdir, "snap1", "alice", "to delete")
    add_comment(cdir, "snap1", "bob", "keep this")
    ok = delete_comment(cdir, "snap1", 0)
    assert ok is True
    comments = get_comments(cdir, "snap1")
    assert len(comments) == 1
    assert comments[0]["text"] == "keep this"


def test_delete_comment_invalid_index_returns_false(cdir):
    add_comment(cdir, "snap1", "alice", "only one")
    assert delete_comment(cdir, "snap1", 5) is False


def test_delete_comment_negative_index_returns_false(cdir):
    add_comment(cdir, "snap1", "alice", "only one")
    assert delete_comment(cdir, "snap1", -1) is False


def test_clear_comments_returns_count(cdir):
    add_comment(cdir, "snap1", "alice", "a")
    add_comment(cdir, "snap1", "bob", "b")
    count = clear_comments(cdir, "snap1")
    assert count == 2


def test_clear_comments_removes_all(cdir):
    add_comment(cdir, "snap1", "alice", "a")
    clear_comments(cdir, "snap1")
    assert get_comments(cdir, "snap1") == []


def test_clear_missing_snapshot_returns_zero(cdir):
    assert clear_comments(cdir, "ghost") == 0


def test_comments_isolated_per_snapshot(cdir):
    add_comment(cdir, "snap1", "alice", "for snap1")
    add_comment(cdir, "snap2", "bob", "for snap2")
    assert len(get_comments(cdir, "snap1")) == 1
    assert len(get_comments(cdir, "snap2")) == 1


def test_format_comments_empty():
    result = format_comments([])
    assert "no comments" in result


def test_format_comments_shows_author_and_text(cdir):
    add_comment(cdir, "snap1", "carol", "hello world")
    comments = get_comments(cdir, "snap1")
    output = format_comments(comments)
    assert "carol" in output
    assert "hello world" in output
    assert "[0]" in output
