"""Integration shim: register the event-hooks sub-command into the main CLI."""

from __future__ import annotations

import argparse

from envforge.cli_event import build_event_parser, cmd_event


def register(subparsers: argparse._SubParsersAction) -> None:
    """Attach the 'event' command to an existing subparsers group."""
    p = build_event_parser(subparsers)
    p.set_defaults(func=cmd_event)


def make_standalone_parser() -> argparse.ArgumentParser:
    """Return a fully-wired standalone parser for the event command."""
    parser = argparse.ArgumentParser(
        prog="envforge-event",
        description="Manage snapshot lifecycle event hooks.",
    )
    subs = parser.add_subparsers(dest="event_action", required=True)
    build_event_parser(subs)
    return parser


if __name__ == "__main__":  # pragma: no cover
    import sys

    _parser = make_standalone_parser()
    _args = _parser.parse_args(sys.argv[1:])
    cmd_event(_args)
