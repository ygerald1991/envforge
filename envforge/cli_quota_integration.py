"""Integration shim to register the quota sub-command with the main CLI."""

from __future__ import annotations

import argparse

from envforge.cli_quota import build_quota_parser, cmd_quota


def register(subparsers: argparse._SubParsersAction) -> None:
    """Attach the 'quota' command group to an existing subparsers action."""
    build_quota_parser(subparsers)


def make_standalone_parser() -> argparse.ArgumentParser:
    """Return a standalone argument parser for the quota command (useful for testing)."""
    parser = argparse.ArgumentParser(
        prog="envforge quota",
        description="Manage snapshot quotas",
    )
    parser.add_argument("--store-dir", default=".envforge", dest="store_dir")
    sub = parser.add_subparsers(dest="quota_action", required=True)

    s = sub.add_parser("set")
    s.add_argument("limit", type=int)
    s.add_argument("--namespace", default=None)

    g = sub.add_parser("get")
    g.add_argument("--namespace", default=None)

    r = sub.add_parser("remove")
    r.add_argument("--namespace", default=None)

    sub.add_parser("list")

    ck = sub.add_parser("check")
    ck.add_argument("count", type=int)
    ck.add_argument("--namespace", default=None)

    parser.set_defaults(func=cmd_quota)
    return parser
