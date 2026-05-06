"""CLI commands for snapshot priority management."""

from __future__ import annotations

import argparse

from envforge.snapshot_priority import (
    get_priority,
    list_by_priority,
    remove_priority,
    set_priority,
)


def cmd_priority(args: argparse.Namespace) -> None:
    sub = args.priority_cmd

    if sub == "set":
        try:
            level = set_priority(args.base_dir, args.snapshot, args.level)
            print(f"Priority for '{args.snapshot}' set to {level}.")
        except ValueError as exc:
            print(f"Error: {exc}")

    elif sub == "get":
        level = get_priority(args.base_dir, args.snapshot)
        if level is None:
            print(f"No priority set for '{args.snapshot}'.")
        else:
            print(f"{args.snapshot}: {level}")

    elif sub == "remove":
        removed = remove_priority(args.base_dir, args.snapshot)
        if removed:
            print(f"Priority removed for '{args.snapshot}'.")
        else:
            print(f"No priority entry found for '{args.snapshot}'.")

    elif sub == "list":
        entries = list_by_priority(args.base_dir)
        if not entries:
            print("No priority entries found.")
        else:
            for name, level in entries:
                print(f"{name}: {level}")


def build_priority_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("priority", help="Manage snapshot priority levels")
    p.add_argument("--base-dir", default=".envforge", dest="base_dir")
    sub = p.add_subparsers(dest="priority_cmd", required=True)

    sp_set = sub.add_parser("set", help="Set priority for a snapshot")
    sp_set.add_argument("snapshot", help="Snapshot name")
    sp_set.add_argument("level", type=int, help="Priority level (1-10)")

    sp_get = sub.add_parser("get", help="Get priority for a snapshot")
    sp_get.add_argument("snapshot", help="Snapshot name")

    sp_rm = sub.add_parser("remove", help="Remove priority for a snapshot")
    sp_rm.add_argument("snapshot", help="Snapshot name")

    sub.add_parser("list", help="List all snapshots ordered by priority")

    p.set_defaults(func=cmd_priority)
