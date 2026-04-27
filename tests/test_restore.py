"""Tests for envforge.restore module."""

import os
import json
import tempfile
import pytest
from unittest.mock import patch
from envforge.restore import restore_to_env, restore_to_shell_script, selective_restore


def _write_snapshot(directory: str, name: str, variables: dict) -> str:
    """Helper: write a snapshot JSON file and return its path."""
    path = os.path.join(directory, f"{name}.json")
    payload = {"name": name, "variables": variables}
    with open(path, "w") as f:
        json.dump(payload, f)
    return path


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def sample_vars():
    return {"APP_ENV": "production", "DB_HOST": "db.prod.internal", "PORT": "5432"}


class TestRestoreToEnv:
    def test_applies_variables_to_os_environ(self, snapshot_dir, sample_vars):
        _write_snapshot(snapshot_dir, "prod", sample_vars)
        applied = restore_to_env("prod", snapshot_dir)
        assert applied == sample_vars
        for key, value in sample_vars.items():
            assert os.environ[key] == value

    def test_returns_applied_dict(self, snapshot_dir, sample_vars):
        _write_snapshot(snapshot_dir, "prod", sample_vars)
        result = restore_to_env("prod", snapshot_dir)
        assert isinstance(result, dict)
        assert set(result.keys()) == set(sample_vars.keys())

    def test_empty_snapshot_applies_nothing(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "empty", {})
        result = restore_to_env("empty", snapshot_dir)
        assert result == {}


class TestRestoreToShellScript:
    def test_bash_script_contains_exports(self, snapshot_dir, sample_vars):
        _write_snapshot(snapshot_dir, "prod", sample_vars)
        script = restore_to_shell_script("prod", snapshot_dir, shell="bash")
        assert "#!/usr/bin/env bash" in script
        assert 'export APP_ENV="production"' in script
        assert 'export PORT="5432"' in script

    def test_fish_script_uses_set_x(self, snapshot_dir, sample_vars):
        _write_snapshot(snapshot_dir, "prod", sample_vars)
        script = restore_to_shell_script("prod", snapshot_dir, shell="fish")
        assert 'set -x APP_ENV "production"' in script
        assert "#!/usr/bin/env bash" not in script

    def test_writes_to_output_path(self, snapshot_dir, sample_vars, tmp_path):
        _write_snapshot(snapshot_dir, "prod", sample_vars)
        out_file = str(tmp_path / "restore.sh")
        restore_to_shell_script("prod", snapshot_dir, shell="bash", output_path=out_file)
        assert os.path.exists(out_file)
        with open(out_file) as f:
            content = f.read()
        assert "export" in content

    def test_unsupported_shell_raises(self, snapshot_dir, sample_vars):
        _write_snapshot(snapshot_dir, "prod", sample_vars)
        with pytest.raises(ValueError, match="Unsupported shell"):
            restore_to_shell_script("prod", snapshot_dir, shell="zsh")

    def test_quotes_are_escaped(self, snapshot_dir):
        vars_with_quotes = {"GREETING": 'say "hello"'}
        _write_snapshot(snapshot_dir, "quoted", vars_with_quotes)
        script = restore_to_shell_script("quoted", snapshot_dir, shell="bash")
        assert '\\"' in script


class TestSelectiveRestore:
    def test_restores_only_specified_keys(self, snapshot_dir, sample_vars):
        _write_snapshot(snapshot_dir, "prod", sample_vars)
        applied = selective_restore("prod", ["APP_ENV", "PORT"], snapshot_dir)
        assert set(applied.keys()) == {"APP_ENV", "PORT"}
        assert "DB_HOST" not in applied

    def test_skips_missing_keys_silently(self, snapshot_dir, sample_vars):
        _write_snapshot(snapshot_dir, "prod", sample_vars)
        applied = selective_restore("prod", ["APP_ENV", "NONEXISTENT"], snapshot_dir)
        assert "NONEXISTENT" not in applied
        assert "APP_ENV" in applied

    def test_empty_key_list_applies_nothing(self, snapshot_dir, sample_vars):
        _write_snapshot(snapshot_dir, "prod", sample_vars)
        applied = selective_restore("prod", [], snapshot_dir)
        assert applied == {}
