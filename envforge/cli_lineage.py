"""CLI commands for snapshot lineage management."""

from __future__ import annotations

import argparse
from typing import Any

from envforge.snapshot_lineage import (
    get_descendants,
    get_lineage,
    record_fork,
    record_merge,
    remove_lineage,
)


def cmd_lineage(args: Any, store_dir: str = ".envforge") -> None:
    sub = args.lineage_sub

    if sub == "fork":
        entry = record_fork(store_dir, args.parent, args.child)
        print(f"Recorded fork: {args.child} <- {args.parent}")

    elif sub == "merge":
        entry = record_merge(store_dir, args.sources, args.result)
        sources_str = ", ".join(args.sources)
        print(f"Recorded merge: {args.result} <- [{sources_str}]")

    elif sub == "show":
        entry = get_lineage(store_dir, args.snapshot)
        if entry is None:
            print(f"No lineage recorded for '{args.snapshot}'.")
        elif entry["type"] == "fork":
            print(f"{args.snapshot} forked from {entry['parent']}")
        elif entry["type"] == "merge":
            sources_str = ", ".join(entry["sources"])
            print(f"{args.snapshot} merged from [{sources_str}]")

    elif sub == "descendants":
        kids = get_descendants(store_dir, args.snapshot)
        if not kids:
            print(f"No descendants found for '{args.snapshot}'.")
        else:
            for name in kids:
                print(f"  {name}")

    elif sub == "remove":
        removed = remove_lineage(store_dir, args.snapshot)
        if removed:
            print(f"Removed lineage record for '{args.snapshot}'.")
        else:
            print(f"No lineage record found for '{args.snapshot}'.")


def build_lineage_parser(subparsers: Any = None) -> argparse.ArgumentParser:
    if subparsers is not None:
        p = subparsers.add_parser("lineage", help="Manage snapshot lineage")
    else:
        p = argparse.ArgumentParser(prog="envforge lineage")

    sp = p.add_subparsers(dest="lineage_sub", required=True)

    fork_p = sp.add_parser("fork", help="Record a fork relationship")
    fork_p.add_argument("parent")
    fork_p.add_argument("child")

    merge_p = sp.add_parser("merge", help="Record a merge relationship")
    merge_p.add_argument("result")
    merge_p.add_argument("sources", nargs="+")

    show_p = sp.add_parser("show", help="Show lineage of a snapshot")
    show_p.add_argument("snapshot")

    desc_p = sp.add_parser("descendants", help="List descendants of a snapshot")
    desc_p.add_argument("snapshot")

    rm_p = sp.add_parser("remove", help="Remove a lineage record")
    rm_p.add_argument("snapshot")

    p.set_defaults(func=cmd_lineage)
    return p
