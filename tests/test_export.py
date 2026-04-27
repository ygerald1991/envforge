"""Tests for envforge.export module."""

import json
import os
import pytest
from pathlib import Path

from envforge.export import export_as_dotenv, export_as_json, export_as_shell, export_snapshot


SAMPLE_VARS = {
    "APP_ENV": "production",
    "DB_HOST": "db.example.com",
    "SECRET_KEY": "s3cr3t with spaces",
    "GREETING": "say \"hello\"",
}


@pytest.fixture()
def snapshot_dir(tmp_path):
    return str(tmp_path)


def _write_snapshot(directory: str, name: str, variables: dict):
    import json
    path = Path(directory) / f"{name}.json"
    path.write_text(json.dumps(variables))


class TestExportAsDotenv:
    def test_contains_all_keys(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "prod", SAMPLE_VARS)
        result = export_as_dotenv("prod", snapshot_dir)
        for key in SAMPLE_VARS:
            assert key in result

    def test_quotes_values_with_spaces(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "prod", SAMPLE_VARS)
        result = export_as_dotenv("prod", snapshot_dir)
        assert 'SECRET_KEY="s3cr3t with spaces"' in result

    def test_plain_values_unquoted(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "prod", SAMPLE_VARS)
        result = export_as_dotenv("prod", snapshot_dir)
        assert "APP_ENV=production" in result

    def test_writes_file_when_output_path_given(self, snapshot_dir, tmp_path):
        _write_snapshot(snapshot_dir, "prod", SAMPLE_VARS)
        out = str(tmp_path / ".env")
        export_as_dotenv("prod", snapshot_dir, output_path=out)
        assert Path(out).exists()
        assert "APP_ENV=production" in Path(out).read_text()

    def test_includes_header_comment(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "prod", SAMPLE_VARS)
        result = export_as_dotenv("prod", snapshot_dir)
        assert "# envforge snapshot: prod" in result


class TestExportAsJson:
    def test_valid_json(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "staging", SAMPLE_VARS)
        result = export_as_json("staging", snapshot_dir)
        parsed = json.loads(result)
        assert parsed["snapshot"] == "staging"
        assert parsed["variables"] == SAMPLE_VARS

    def test_writes_file(self, snapshot_dir, tmp_path):
        _write_snapshot(snapshot_dir, "staging", SAMPLE_VARS)
        out = str(tmp_path / "snap.json")
        export_as_json("staging", snapshot_dir, output_path=out)
        assert Path(out).exists()


class TestExportAsShell:
    def test_contains_export_statements(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "dev", SAMPLE_VARS)
        result = export_as_shell("dev", snapshot_dir)
        assert "export APP_ENV='production'" in result

    def test_shebang_present(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "dev", SAMPLE_VARS)
        result = export_as_shell("dev", snapshot_dir)
        assert result.startswith("#!/usr/bin/env sh")

    def test_file_is_executable(self, snapshot_dir, tmp_path):
        _write_snapshot(snapshot_dir, "dev", SAMPLE_VARS)
        out = str(tmp_path / "env.sh")
        export_as_shell("dev", snapshot_dir, output_path=out)
        assert os.access(out, os.X_OK)


class TestExportSnapshot:
    def test_dispatches_dotenv(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "prod", SAMPLE_VARS)
        result = export_snapshot("prod", snapshot_dir, fmt="dotenv")
        assert "APP_ENV=production" in result

    def test_dispatches_json(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "prod", SAMPLE_VARS)
        result = export_snapshot("prod", snapshot_dir, fmt="json")
        assert json.loads(result)["snapshot"] == "prod"

    def test_dispatches_shell(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "prod", SAMPLE_VARS)
        result = export_snapshot("prod", snapshot_dir, fmt="shell")
        assert "export" in result

    def test_raises_on_unknown_format(self, snapshot_dir):
        _write_snapshot(snapshot_dir, "prod", SAMPLE_VARS)
        with pytest.raises(ValueError, match="Unknown export format"):
            export_snapshot("prod", snapshot_dir, fmt="yaml")
