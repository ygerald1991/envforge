"""Integration helpers to register the permission sub-command."""

from __future__ import annotations

import argparse

from envforge.cli_permission import build_permission_parser, cmd_permission


def register(subparsers: argparse._SubParsersAction) -> None:
    """Attach the 'permission' command to an existing subparser group."""
    build_permission_parser(subparsers)


def make_standalone_parser() -> argparse.ArgumentParser:
    """Return a standalone parser useful for testing or direct invocation."""
    parser = argparse.ArgumentParser(
        prog="envforge-permission",
        description="Manage per-user permissions on snapshots.",
    )
    sub = parser.add_subparsers(dest="perm_cmd", required=True)
    build_permission_parser(sub)
    return parser
