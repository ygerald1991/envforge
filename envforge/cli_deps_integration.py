"""Integration helpers to register snapshot deps commands into the main CLI."""

import argparse
from envforge.cli_deps import build_deps_parser, cmd_deps


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'deps' subcommand into an existing subparsers group."""
    build_deps_parser(subparsers)


def make_standalone_parser() -> argparse.ArgumentParser:
    """Return a standalone argument parser for the deps command."""
    parser = argparse.ArgumentParser(
        prog="envforge-deps",
        description="Manage snapshot dependency relationships.",
    )
    parser.add_argument(
        "--base-dir",
        default=".",
        dest="base_dir",
        help="Base directory where .envforge data is stored (default: current dir).",
    )
    sub = parser.add_subparsers(dest="deps_action", required=True)

    add_p = sub.add_parser("add", help="Add a dependency between two snapshots")
    add_p.add_argument("snapshot", help="The dependent snapshot")
    add_p.add_argument("depends_on", help="The snapshot it depends on")

    rm_p = sub.add_parser("remove", help="Remove a dependency")
    rm_p.add_argument("snapshot")
    rm_p.add_argument("depends_on")

    ls_p = sub.add_parser("list", help="List direct dependencies of a snapshot")
    ls_p.add_argument("snapshot")

    dep_p = sub.add_parser("dependents", help="List snapshots that depend on a given one")
    dep_p.add_argument("snapshot")

    sub.add_parser("all", help="Display the full dependency graph")

    parser.set_defaults(func=cmd_deps)
    return parser
