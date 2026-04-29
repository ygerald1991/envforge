"""Tests for envforge.template."""

from __future__ import annotations

import json
import pytest

from envforge.template import (
    apply_template,
    create_template,
    get_placeholders,
    list_templates,
    load_template,
)


@pytest.fixture()
def tdir(tmp_path):
    return str(tmp_path)


def _tmpl(tdir, name="base", vars=None):
    v = vars or {"HOST": "<HOST>", "PORT": "8080", "SECRET": "<SECRET>"}
    create_template(v, name, tdir)
    return v


class TestCreateAndLoad:
    def test_creates_json_file(self, tdir):
        _tmpl(tdir)
        path = __import__("pathlib").Path(tdir) / "templates" / "base.json"
        assert path.exists()

    def test_load_returns_same_dict(self, tdir):
        original = _tmpl(tdir)
        loaded = load_template("base", tdir)
        assert loaded == original

    def test_load_missing_raises(self, tdir):
        with pytest.raises(FileNotFoundError):
            load_template("ghost", tdir)


class TestListTemplates:
    def test_empty_returns_empty_list(self, tdir):
        assert list_templates(tdir) == []

    def test_returns_all_names(self, tdir):
        _tmpl(tdir, "alpha")
        _tmpl(tdir, "beta")
        assert list_templates(tdir) == ["alpha", "beta"]

    def test_names_are_sorted(self, tdir):
        for n in ["zzz", "aaa", "mmm"]:
            _tmpl(tdir, n)
        assert list_templates(tdir) == ["aaa", "mmm", "zzz"]


class TestGetPlaceholders:
    def test_identifies_placeholder_keys(self, tdir):
        tmpl = {"A": "<A>", "B": "real", "C": "<C>"}
        assert get_placeholders(tmpl) == ["A", "C"]

    def test_no_placeholders(self):
        assert get_placeholders({"X": "1", "Y": "2"}) == []

    def test_partial_angle_bracket_not_placeholder(self):
        assert get_placeholders({"X": "<not closed"}) == []


class TestApplyTemplate:
    def test_substitutes_by_placeholder_name(self):
        tmpl = {"HOST": "<HOST>", "PORT": "9000"}
        result = apply_template(tmpl, {"HOST": "localhost"})
        assert result["HOST"] == "localhost"
        assert result["PORT"] == "9000"

    def test_substitutes_by_key_name(self):
        tmpl = {"DB_PASS": "<DB_PASS>"}
        result = apply_template(tmpl, {"DB_PASS": "secret"})
        assert result["DB_PASS"] == "secret"

    def test_unresolved_raises_by_default(self):
        tmpl = {"X": "<X>"}
        with pytest.raises(ValueError, match="Unresolved"):
            apply_template(tmpl, {})

    def test_allow_partial_skips_raise(self):
        tmpl = {"X": "<X>", "Y": "<Y>"}
        result = apply_template(tmpl, {"X": "filled"}, allow_partial=True)
        assert result["X"] == "filled"
        assert result["Y"] == "<Y>"

    def test_non_placeholder_values_unchanged(self):
        tmpl = {"STATIC": "value"}
        result = apply_template(tmpl, {"STATIC": "other"})
        assert result["STATIC"] == "value"
