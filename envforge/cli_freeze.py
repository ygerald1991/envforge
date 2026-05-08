"""CLI commands for snapshot freeze/unfreeze."""

from __future__ import annotations

import argparse
from envforge.snapshot_freeze import (
    freeze_snapshot,
    unfreeze_snapshot,
    is_frozen,
    list_frozen,
)


def cmd_freeze(args: argparse.Namespace) -> None:
    action = args.freeze_action

    if action == "add":
        freeze_snapshot(args.store_dir, args.snapshot)
        print(f"Snapshot '{args.snapshot}' is now frozen.")

    elif action == "remove":
        if not is_frozen(args.store_dir, args.snapshot):
            print(f"Snapshot '{args.snapshot}' is not frozen.")
            return
        unfreeze_snapshot(args.store_dir, args.snapshot)
        print(f"Snapshot '{args.snapshot}' has been unfrozen.")

    elif action == "status":
        state = "frozen" if is_frozen(args.store_dir, args.snapshot) else "not frozen"
        print(f"Snapshot '{args.snapshot}' is {state}.")

    elif action == "list":
        frozen = list_frozen(args.store_dir)
        if not frozen:
            print("No frozen snapshots.")
        else:
            for name in frozen:
                print(name)


def build_freeze_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser("freeze", help="Freeze or unfreeze snapshots")
    parser.add_argument("--store-dir", default=".envforge", dest="store_dir")
    sub = parser.add_subparsers(dest="freeze_action", required=True)

    p_add = sub.add_parser("add", help="Freeze a snapshot")
    p_add.add_argument("snapshot", help="Snapshot name to freeze")

    p_rm = sub.add_parser("remove", help="Unfreeze a snapshot")
    p_rm.add_argument("snapshot", help="Snapshot name to unfreeze")

    p_st = sub.add_parser("status", help="Check freeze status of a snapshot")
    p_st.add_argument("snapshot", help="Snapshot name")

    sub.add_parser("list", help="List all frozen snapshots")

    parser.set_defaults(func=cmd_freeze)
