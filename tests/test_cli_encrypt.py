"""Tests for envforge.cli_encrypt."""

import json
import argparse
import pytest
from pathlib import Path
from unittest.mock import patch

pytest.importorskip("cryptography", reason="cryptography package not installed")

from envforge.encrypt import generate_key, save_encrypted_snapshot
from envforge.cli_encrypt import cmd_encrypt, cmd_decrypt, cmd_keygen


SAMPLE_SNAP = {"vars": {"STAGE": "dev", "PORT": "8080"}, "name": "dev"}


def _write_json_snapshot(snap_dir: Path, name: str, data: dict) -> Path:
    path = snap_dir / f"{name}.json"
    path.write_text(json.dumps(data))
    return path


@pytest.fixture()
def snap_dir(tmp_path):
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def _args(**kwargs):
    base = {"snapshot_dir": None, "key": None, "output": None}
    base.update(kwargs)
    return argparse.Namespace(**base)


class TestCmdEncrypt:
    def test_creates_enc_file(self, snap_dir, capsys):
        _write_json_snapshot(snap_dir, "dev", SAMPLE_SNAP)
        args = _args(name="dev", snapshot_dir=str(snap_dir))
        with patch("envforge.cli_encrypt._ensure_snapshot_dir", return_value=snap_dir):
            cmd_encrypt(args)
        assert (snap_dir / "dev.enc").exists()

    def test_prints_generated_key_when_none_provided(self, snap_dir, capsys):
        _write_json_snapshot(snap_dir, "dev", SAMPLE_SNAP)
        args = _args(name="dev", snapshot_dir=str(snap_dir))
        with patch("envforge.cli_encrypt._ensure_snapshot_dir", return_value=snap_dir):
            cmd_encrypt(args)
        out = capsys.readouterr().out
        assert "Generated key" in out

    def test_uses_provided_key(self, snap_dir, capsys):
        _write_json_snapshot(snap_dir, "dev", SAMPLE_SNAP)
        key = generate_key()
        args = _args(name="dev", key=key, snapshot_dir=str(snap_dir))
        with patch("envforge.cli_encrypt._ensure_snapshot_dir", return_value=snap_dir):
            cmd_encrypt(args)
        out = capsys.readouterr().out
        assert "Generated key" not in out
        assert (snap_dir / "dev.enc").exists()


class TestCmdDecrypt:
    def test_prints_json_to_stdout(self, snap_dir, capsys):
        key = generate_key()
        save_encrypted_snapshot(SAMPLE_SNAP, snap_dir / "dev.enc", key)
        args = _args(name="dev", key=key, snapshot_dir=str(snap_dir))
        with patch("envforge.cli_encrypt._ensure_snapshot_dir", return_value=snap_dir):
            cmd_decrypt(args)
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert parsed == SAMPLE_SNAP

    def test_writes_to_output_file(self, snap_dir, tmp_path, capsys):
        key = generate_key()
        save_encrypted_snapshot(SAMPLE_SNAP, snap_dir / "dev.enc", key)
        out_file = tmp_path / "out.json"
        args = _args(name="dev", key=key, output=str(out_file), snapshot_dir=str(snap_dir))
        with patch("envforge.cli_encrypt._ensure_snapshot_dir", return_value=snap_dir):
            cmd_decrypt(args)
        assert out_file.exists()
        assert json.loads(out_file.read_text()) == SAMPLE_SNAP


class TestCmdKeygen:
    def test_prints_key(self, capsys):
        cmd_keygen(argparse.Namespace())
        out = capsys.readouterr().out.strip()
        assert len(out) > 20
