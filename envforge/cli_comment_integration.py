"""Integration helpers to register comment commands with the main CLI."""

import argparse
from envforge.cli_comment import build_comment_parser, cmd_comment


def register(subparsers: argparse._SubParsersAction) -> None:
    """Attach the 'comment' subcommand to an existing subparser group."""
    build_comment_parser(subparsers)


def make_standalone_parser() -> argparse.ArgumentParser:
    """Return a fully standalone parser for the comment feature."""
    parser = argparse.ArgumentParser(
        prog="envforge-comment",
        description="Manage inline comments on envforge snapshots.",
    )
    sub = parser.add_subparsers(dest="comment_action", required=True)

    add_p = sub.add_parser("add", help="Add a comment to a snapshot")
    add_p.add_argument("snapshot", help="Snapshot name")
    add_p.add_argument("author", help="Author name")
    add_p.add_argument("text", help="Comment body")

    list_p = sub.add_parser("list", help="List all comments on a snapshot")
    list_p.add_argument("snapshot", help="Snapshot name")

    del_p = sub.add_parser("delete", help="Delete a comment by its index")
    del_p.add_argument("snapshot", help="Snapshot name")
    del_p.add_argument("index", type=int, help="Zero-based comment index")

    clr_p = sub.add_parser("clear", help="Remove all comments from a snapshot")
    clr_p.add_argument("snapshot", help="Snapshot name")

    parser.set_defaults(func=cmd_comment)
    return parser


if __name__ == "__main__":  # pragma: no cover
    import sys

    _parser = make_standalone_parser()
    _args = _parser.parse_args()
    _args.func(_args)
