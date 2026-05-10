"""Tests for envforge.snapshot_compliance."""

from __future__ import annotations

import pytest

from envforge.snapshot_compliance import (
    check_compliance,
    get_compliance_rule,
    list_compliance_rules,
    remove_compliance_rule,
    set_compliance_rule,
)


@pytest.fixture()
def cdir(tmp_path):
    return str(tmp_path)


# --- set / get ---

def test_set_and_get_rule(cdir):
    set_compliance_rule(cdir, "prod", {"required_prefix": "prod_"})
    rule = get_compliance_rule(cdir, "prod")
    assert rule == {"required_prefix": "prod_"}


def test_get_missing_rule_returns_none(cdir):
    assert get_compliance_rule(cdir, "nonexistent") is None


def test_overwrite_existing_rule(cdir):
    set_compliance_rule(cdir, "r", {"max_keys": 10})
    set_compliance_rule(cdir, "r", {"max_keys": 20})
    assert get_compliance_rule(cdir, "r")["max_keys"] == 20


def test_unknown_field_raises(cdir):
    with pytest.raises(ValueError, match="Unknown rule fields"):
        set_compliance_rule(cdir, "bad", {"bogus_field": "x"})


# --- list ---

def test_list_returns_all_rules(cdir):
    set_compliance_rule(cdir, "a", {"max_keys": 5})
    set_compliance_rule(cdir, "b", {"required_prefix": "dev_"})
    rules = list_compliance_rules(cdir)
    assert set(rules.keys()) == {"a", "b"}


def test_list_empty_store_returns_empty(cdir):
    assert list_compliance_rules(cdir) == {}


# --- remove ---

def test_remove_existing_rule(cdir):
    set_compliance_rule(cdir, "r", {"max_keys": 3})
    assert remove_compliance_rule(cdir, "r") is True
    assert get_compliance_rule(cdir, "r") is None


def test_remove_missing_rule_returns_false(cdir):
    assert remove_compliance_rule(cdir, "ghost") is False


# --- check_compliance ---

def test_check_required_prefix_pass(cdir):
    set_compliance_rule(cdir, "r", {"required_prefix": "prod_"})
    violations = check_compliance(cdir, "prod_snap", {"A": "1"}, "r")
    assert violations == []


def test_check_required_prefix_fail(cdir):
    set_compliance_rule(cdir, "r", {"required_prefix": "prod_"})
    violations = check_compliance(cdir, "dev_snap", {"A": "1"}, "r")
    assert any("prod_" in v for v in violations)


def test_check_key_pattern_pass(cdir):
    set_compliance_rule(cdir, "r", {"key_pattern": "^[A-Z_]+$"})
    violations = check_compliance(cdir, "snap", {"MY_VAR": "val"}, "r")
    assert violations == []


def test_check_key_pattern_fail(cdir):
    set_compliance_rule(cdir, "r", {"key_pattern": "^[A-Z_]+$"})
    violations = check_compliance(cdir, "snap", {"bad-key": "val"}, "r")
    assert any("bad-key" in v for v in violations)


def test_check_max_keys_pass(cdir):
    set_compliance_rule(cdir, "r", {"max_keys": 3})
    violations = check_compliance(cdir, "snap", {"A": "1", "B": "2"}, "r")
    assert violations == []


def test_check_max_keys_fail(cdir):
    set_compliance_rule(cdir, "r", {"max_keys": 2})
    violations = check_compliance(cdir, "snap", {"A": "1", "B": "2", "C": "3"}, "r")
    assert any("max_keys" in v for v in violations)


def test_check_multiple_violations(cdir):
    set_compliance_rule(cdir, "r", {"required_prefix": "prod_", "max_keys": 1})
    violations = check_compliance(cdir, "dev_snap", {"A": "1", "B": "2"}, "r")
    assert len(violations) == 2


def test_check_missing_rule_raises(cdir):
    with pytest.raises(KeyError):
        check_compliance(cdir, "snap", {}, "no_such_rule")
