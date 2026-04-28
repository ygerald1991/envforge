"""CLI commands for pinning and unpinning snapshots."""

import argparse
from envforge.pin import pin_snapshot, unpin_snapshot, is_pinned, list_pinned


def cmd_pin(args: argparse.Namespace) -> None:
    action = args.pin_action
    snapshot_dir = args.snapshot_dir

    if action == "add":
        pin_snapshot(snapshot_dir, args.name)
        print(f"Pinned snapshot '{args.name}'.")

    elif action == "remove":
        if not is_pinned(snapshot_dir, args.name):
            print(f"Snapshot '{args.name}' is not pinned.")
            return
        unpin_snapshot(snapshot_dir, args.name)
        print(f"Unpinned snapshot '{args.name}'.")

    elif action == "list":
        pins = list_pinned(snapshot_dir)
        if not pins:
            print("No pinned snapshots.")
        else:
            for name in pins:
                print(name)

    elif action == "check":
        status = "pinned" if is_pinned(snapshot_dir, args.name) else "not pinned"
        print(f"Snapshot '{args.name}' is {status}.")


def build_pin_parser(subparsers: argparse._SubParsersAction) -> None:
    pin_parser = subparsers.add_parser("pin", help="Pin or unpin snapshots")
    pin_parser.add_argument(
        "--snapshot-dir", default=".envforge", dest="snapshot_dir"
    )
    pin_sub = pin_parser.add_subparsers(dest="pin_action", required=True)

    add_p = pin_sub.add_parser("add", help="Pin a snapshot")
    add_p.add_argument("name", help="Snapshot name to pin")

    rem_p = pin_sub.add_parser("remove", help="Unpin a snapshot")
    rem_p.add_argument("name", help="Snapshot name to unpin")

    pin_sub.add_parser("list", help="List all pinned snapshots")

    chk_p = pin_sub.add_parser("check", help="Check if a snapshot is pinned")
    chk_p.add_argument("name", help="Snapshot name to check")

    pin_parser.set_defaults(func=cmd_pin)
