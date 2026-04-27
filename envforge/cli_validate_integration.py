"""Thin integration shim: registers validate commands into the main CLI.

Import this module in cli.py (or the top-level entry point) to make
`envforge validate` available alongside the other sub-commands.

Example usage in cli.py::

    from envforge.cli_validate_integration import register
    register(subparsers)
"""

import argparse

from envforge.cli_validate import build_validate_parser


def register(subparsers: argparse.Action) -> None:
    """Register the validate sub-command onto *subparsers*."""
    build_validate_parser(subparsers)


def make_standalone_parser() -> argparse.ArgumentParser:
    """Return a standalone argument parser for the validate command.

    Useful for testing or running the validator as a standalone tool::

        parser = make_standalone_parser()
        args = parser.parse_args(["prod", "--require", "DB_URL"])
    """
    parser = argparse.ArgumentParser(
        prog="envforge-validate",
        description="Validate an envforge snapshot against a set of rules.",
    )
    subparsers = parser.add_subparsers(dest="command")
    build_validate_parser(subparsers)
    return parser


if __name__ == "__main__":  # pragma: no cover
    import sys

    _parser = make_standalone_parser()
    _args = _parser.parse_args(sys.argv[1:])
    if hasattr(_args, "func"):
        _args.func(_args)
    else:
        _parser.print_help()
