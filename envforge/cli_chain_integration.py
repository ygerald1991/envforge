"""Register the chain sub-command with the main envforge CLI."""

from __future__ import annotations

import argparse

from envforge.cli_chain import build_chain_parser


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach the 'chain' command group to an existing subparsers action."""
    build_chain_parser(subparsers)


def make_standalone_parser() -> argparse.ArgumentParser:
    """Return a self-contained parser for the chain commands (useful for testing)."""
    parser = argparse.ArgumentParser(
        prog="envforge chain",
        description="Manage snapshot parent/child lineage chains.",
    )
    sub = parser.add_subparsers(dest="chain_sub", required=True)
    build_chain_parser(sub)
    return parser
