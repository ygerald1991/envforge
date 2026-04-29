"""Tests for envforge.cli_template."""

from __future__ import annotations

import argparse
import json
import types

import pytest

from envforge.cli_template import cmd_template
from envforge.template import create_template


def _args(tdir, template_cmd, **kwargs):
    ns = argparse.Namespace(dir=tdir, template_cmd=template_cmd, **kwargs)
    return ns


@pytest.fixture()
def tdir(tmp_path):
    return str(tmp_path)


class TestCmdTemplateCreate:
    def test_prints_confirmation(self, tdir, capsys):
        a = _args(tdir, "create", name="dev", vars_json=json.dumps({"HOST": "<HOST>"}))
        cmd_template(a)
        out = capsys.readouterr().out
        assert "dev" in out
        assert "saved" in out.lower()

    def test_file_is_created(self, tdir):
        a = _args(tdir, "create", name="prod", vars_json=json.dumps({"K": "V"}))
        cmd_template(a)
        import pathlib
        assert (pathlib.Path(tdir) / "templates" / "prod.json").exists()


class TestCmdTemplateList:
    def test_empty_message(self, tdir, capsys):
        cmd_template(_args(tdir, "list"))
        assert "No templates" in capsys.readouterr().out

    def test_shows_template_names(self, tdir, capsys):
        create_template({"A": "1"}, "alpha", tdir)
        create_template({"B": "2"}, "beta", tdir)
        cmd_template(_args(tdir, "list"))
        out = capsys.readouterr().out
        assert "alpha" in out
        assert "beta" in out


class TestCmdTemplateShow:
    def test_prints_json(self, tdir, capsys):
        create_template({"X": "<X>", "Y": "static"}, "mytempl", tdir)
        cmd_template(_args(tdir, "show", name="mytempl"))
        out = capsys.readouterr().out
        data = json.loads(out.split("\n\n")[0])
        assert data["X"] == "<X>"

    def test_shows_placeholder_list(self, tdir, capsys):
        create_template({"P": "<P>"}, "t", tdir)
        cmd_template(_args(tdir, "show", name="t"))
        out = capsys.readouterr().out
        assert "Placeholders" in out
        assert "P" in out


class TestCmdTemplateApply:
    def test_prints_resolved_json(self, tdir, capsys):
        create_template({"HOST": "<HOST>", "PORT": "80"}, "srv", tdir)
        a = _args(
            tdir, "apply",
            name="srv",
            subs_json=json.dumps({"HOST": "example.com"}),
            partial=False,
        )
        cmd_template(a)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["HOST"] == "example.com"
        assert data["PORT"] == "80"

    def test_partial_flag_allows_unresolved(self, tdir, capsys):
        create_template({"A": "<A>", "B": "<B>"}, "partial", tdir)
        a = _args(tdir, "apply", name="partial", subs_json="{}", partial=True)
        cmd_template(a)  # should not raise
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["A"] == "<A>"
