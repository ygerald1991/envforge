"""Tests for envforge.snapshot_notes."""

import pytest
from envforge.snapshot_notes import (
    set_note,
    get_note,
    remove_note,
    list_notes,
    format_notes,
)


@pytest.fixture
def ndir(tmp_path):
    return str(tmp_path)


def test_set_and_get_note(ndir):
    set_note(ndir, "snap1", "initial dev snapshot")
    assert get_note(ndir, "snap1") == "initial dev snapshot"


def test_get_missing_note_returns_none(ndir):
    assert get_note(ndir, "nonexistent") is None


def test_overwrite_existing_note(ndir):
    set_note(ndir, "snap1", "old note")
    set_note(ndir, "snap1", "new note")
    assert get_note(ndir, "snap1") == "new note"


def test_remove_existing_note(ndir):
    set_note(ndir, "snap1", "some note")
    result = remove_note(ndir, "snap1")
    assert result is True
    assert get_note(ndir, "snap1") is None


def test_remove_missing_note_returns_false(ndir):
    result = remove_note(ndir, "ghost")
    assert result is False


def test_list_notes_empty(ndir):
    assert list_notes(ndir) == {}


def test_list_notes_multiple(ndir):
    set_note(ndir, "alpha", "note A")
    set_note(ndir, "beta", "note B")
    notes = list_notes(ndir)
    assert notes == {"alpha": "note A", "beta": "note B"}


def test_remove_does_not_affect_other_notes(ndir):
    set_note(ndir, "snap1", "keep")
    set_note(ndir, "snap2", "delete me")
    remove_note(ndir, "snap2")
    assert get_note(ndir, "snap1") == "keep"
    assert get_note(ndir, "snap2") is None


def test_format_notes_empty():
    assert format_notes({}) == "No notes found."


def test_format_notes_contains_name_and_text():
    output = format_notes({"snap1": "hello world"})
    assert "snap1" in output
    assert "hello world" in output


def test_format_notes_sorted_order():
    notes = {"zzz": "last", "aaa": "first"}
    output = format_notes(notes)
    assert output.index("aaa") < output.index("zzz")


def test_notes_persisted_across_calls(ndir):
    set_note(ndir, "persist", "should survive")
    # simulate a fresh load by calling list_notes independently
    all_notes = list_notes(ndir)
    assert all_notes["persist"] == "should survive"
