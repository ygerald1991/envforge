"""Tests for envforge.cli_compliance."""

from __future__ import annotations

import argparse
import json
import types

import pytest

from envforge.cli_compliance import cmd_compliance, build_compliance_parser
from envforge.snapshot_compliance import set_compliance_rule, get_compliance_rule


@pytest.fixture()
def cdir(tmp_path):
    return str(tmp_path)


def _make_args(base_dir, compliance_sub, **kwargs):
    ns = argparse.Namespace(
        base_dir=base_dir,
        compliance_sub=compliance_sub,
        required_prefix="",
        key_pattern="",
        max_keys=None,
        rule_name=None,
        snapshot_name=None,
        variables_json=None,
        **kwargs,
    )
    return ns


def test_set_prints_confirmation(cdir, capsys):
    args = _make_args(cdir, "set", rule_name="prod", required_prefix="prod_")
    cmd_compliance(args)
    out = capsys.readouterr().out
    assert "prod" in out and "saved" in out


def test_set_persists_rule(cdir):
    args = _make_args(cdir, "set", rule_name="r", max_keys=5)
    cmd_compliance(args)
    assert get_compliance_rule(cdir, "r") == {"max_keys": 5}


def test_set_no_fields_exits(cdir):
    args = _make_args(cdir, "set", rule_name="r")
    with pytest.raises(SystemExit):
        cmd_compliance(args)


def test_get_existing_rule(cdir, capsys):
    set_compliance_rule(cdir, "r", {"max_keys": 7})
    args = _make_args(cdir, "get", rule_name="r")
    cmd_compliance(args)
    out = capsys.readouterr().out
    assert "max_keys" in out


def test_get_missing_rule(cdir, capsys):
    args = _make_args(cdir, "get", rule_name="ghost")
    cmd_compliance(args)
    assert "No rule found" in capsys.readouterr().out


def test_list_shows_all_rules(cdir, capsys):
    set_compliance_rule(cdir, "a", {"max_keys": 2})
    set_compliance_rule(cdir, "b", {"required_prefix": "dev_"})
    args = _make_args(cdir, "list")
    cmd_compliance(args)
    out = capsys.readouterr().out
    assert "a" in out and "b" in out


def test_list_empty(cdir, capsys):
    args = _make_args(cdir, "list")
    cmd_compliance(args)
    assert "No compliance rules" in capsys.readouterr().out


def test_remove_existing(cdir, capsys):
    set_compliance_rule(cdir, "r", {"max_keys": 1})
    args = _make_args(cdir, "remove", rule_name="r")
    cmd_compliance(args)
    assert "removed" in capsys.readouterr().out


def test_remove_missing(cdir, capsys):
    args = _make_args(cdir, "remove", rule_name="ghost")
    cmd_compliance(args)
    assert "not found" in capsys.readouterr().out


def test_check_compliant(cdir, capsys):
    set_compliance_rule(cdir, "r", {"max_keys": 5})
    args = _make_args(
        cdir, "check",
        rule_name="r",
        snapshot_name="snap",
        variables_json=json.dumps({"A": "1"}),
    )
    cmd_compliance(args)
    assert "Compliant" in capsys.readouterr().out


def test_check_violations_exits_2(cdir):
    set_compliance_rule(cdir, "r", {"required_prefix": "prod_"})
    args = _make_args(
        cdir, "check",
        rule_name="r",
        snapshot_name="dev_snap",
        variables_json=json.dumps({"A": "1"}),
    )
    with pytest.raises(SystemExit) as exc:
        cmd_compliance(args)
    assert exc.value.code == 2


def test_build_compliance_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    build_compliance_parser(subs)
    args = parser.parse_args(["compliance", "list"])
    assert args.compliance_sub == "list"
