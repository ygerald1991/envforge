"""CLI commands for snapshot status management."""

from __future__ import annotations

import argparse
from typing import Optional

from envforge.snapshot_status import (
    VALID_STATUSES,
    get_all_statuses,
    get_status,
    list_by_status,
    remove_status,
    set_status,
)


def cmd_status(args: argparse.Namespace, store_dir: Optional[str] = None) -> None:
    sdir = store_dir or args.store_dir

    if args.status_cmd == "set":
        try:
            result = set_status(sdir, args.snapshot, args.status)
            print(f"Status for '{args.snapshot}' set to '{result}'.")
        except ValueError as exc:
            print(f"Error: {exc}")

    elif args.status_cmd == "get":
        status = get_status(sdir, args.snapshot)
        if status is None:
            print(f"No status set for '{args.snapshot}'.")
        else:
            print(f"{args.snapshot}: {status}")

    elif args.status_cmd == "remove":
        removed = remove_status(sdir, args.snapshot)
        if removed:
            print(f"Status removed for '{args.snapshot}'.")
        else:
            print(f"No status entry found for '{args.snapshot}'.")

    elif args.status_cmd == "list":
        if args.filter:
            try:
                names = list_by_status(sdir, args.filter)
            except ValueError as exc:
                print(f"Error: {exc}")
                return
            if not names:
                print(f"No snapshots with status '{args.filter}'.")
            else:
                for name in sorted(names):
                    print(f"  {name}")
        else:
            index = get_all_statuses(sdir)
            if not index:
                print("No status entries found.")
            else:
                for name, status in sorted(index.items()):
                    print(f"  {name}: {status}")


def build_status_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser("status", help="Manage snapshot status labels")
    p.add_argument("--store-dir", default=".envforge", help="Snapshot store directory")
    sub = p.add_subparsers(dest="status_cmd", required=True)

    s_set = sub.add_parser("set", help="Set status for a snapshot")
    s_set.add_argument("snapshot")
    s_set.add_argument("status", choices=sorted(VALID_STATUSES))

    s_get = sub.add_parser("get", help="Get status of a snapshot")
    s_get.add_argument("snapshot")

    s_rm = sub.add_parser("remove", help="Remove status from a snapshot")
    s_rm.add_argument("snapshot")

    s_ls = sub.add_parser("list", help="List snapshot statuses")
    s_ls.add_argument("--filter", metavar="STATUS", help="Filter by status value")

    p.set_defaults(func=cmd_status)
    return p
