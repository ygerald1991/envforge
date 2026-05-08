"""Integration shim: registers the lineage sub-command with the main CLI."""

from __future__ import annotations

import argparse

from envforge.cli_lineage import build_lineage_parser, cmd_lineage


def register(subparsers: argparse._SubParsersAction) -> None:
    """Attach the lineage command group to an existing subparsers action."""
    build_lineage_parser(subparsers)


def make_standalone_parser() -> argparse.ArgumentParser:
    """Return a fully self-contained argument parser for standalone use."""
    parser = argparse.ArgumentParser(
        prog="envforge-lineage",
        description="Manage snapshot lineage (forks and merges).",
    )
    sp = parser.add_subparsers(dest="lineage_sub", required=True)
    build_lineage_parser(sp)
    return parser
