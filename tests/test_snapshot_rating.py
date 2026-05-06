"""Tests for envforge.snapshot_rating."""

import pytest
from envforge.snapshot_rating import (
    set_rating,
    get_rating,
    remove_rating,
    list_ratings,
    top_rated,
)


@pytest.fixture()
def rdir(tmp_path):
    return str(tmp_path)


def test_set_and_get_rating(rdir):
    entry = set_rating(rdir, "snap_a", 4, "pretty good")
    assert entry["stars"] == 4
    assert entry["comment"] == "pretty good"
    result = get_rating(rdir, "snap_a")
    assert result == {"stars": 4, "comment": "pretty good"}


def test_get_missing_rating_returns_none(rdir):
    assert get_rating(rdir, "nonexistent") is None


def test_overwrite_existing_rating(rdir):
    set_rating(rdir, "snap_a", 3)
    set_rating(rdir, "snap_a", 5, "updated")
    result = get_rating(rdir, "snap_a")
    assert result["stars"] == 5
    assert result["comment"] == "updated"


def test_rating_out_of_range_raises(rdir):
    with pytest.raises(ValueError):
        set_rating(rdir, "snap_a", 0)
    with pytest.raises(ValueError):
        set_rating(rdir, "snap_a", 6)


def test_rating_boundary_values_accepted(rdir):
    set_rating(rdir, "low", 1)
    set_rating(rdir, "high", 5)
    assert get_rating(rdir, "low")["stars"] == 1
    assert get_rating(rdir, "high")["stars"] == 5


def test_remove_existing_rating(rdir):
    set_rating(rdir, "snap_a", 3)
    removed = remove_rating(rdir, "snap_a")
    assert removed is True
    assert get_rating(rdir, "snap_a") is None


def test_remove_missing_rating_returns_false(rdir):
    assert remove_rating(rdir, "ghost") is False


def test_list_ratings_empty(rdir):
    assert list_ratings(rdir) == {}


def test_list_ratings_multiple(rdir):
    set_rating(rdir, "a", 2)
    set_rating(rdir, "b", 4)
    result = list_ratings(rdir)
    assert set(result.keys()) == {"a", "b"}


def test_top_rated_order(rdir):
    set_rating(rdir, "snap_c", 3)
    set_rating(rdir, "snap_a", 5)
    set_rating(rdir, "snap_b", 4)
    ranked = top_rated(rdir)
    assert ranked[0]["snapshot"] == "snap_a"
    assert ranked[1]["snapshot"] == "snap_b"
    assert ranked[2]["snapshot"] == "snap_c"


def test_top_rated_respects_limit(rdir):
    for i in range(1, 7):
        set_rating(rdir, f"snap_{i}", (i % 5) + 1)
    result = top_rated(rdir, limit=3)
    assert len(result) == 3


def test_comment_defaults_to_empty_string(rdir):
    set_rating(rdir, "snap_x", 3)
    result = get_rating(rdir, "snap_x")
    assert result["comment"] == ""
