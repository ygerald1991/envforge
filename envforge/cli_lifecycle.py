"""CLI commands for snapshot lifecycle state management."""

import argparse
from envforge.snapshot_lifecycle import (
    set_lifecycle_state,
    get_lifecycle_state,
    list_by_state,
    remove_lifecycle_state,
    VALID_STATES,
)


def cmd_lifecycle(args: argparse.Namespace) -> None:
    store = args.store_dir

    if args.lifecycle_cmd == "set":
        entry = set_lifecycle_state(store, args.snapshot, args.state)
        print(f"Lifecycle state for '{args.snapshot}' set to '{args.state}' at {entry['updated_at']}.")

    elif args.lifecycle_cmd == "get":
        state = get_lifecycle_state(store, args.snapshot)
        if state is None:
            print(f"No lifecycle state set for '{args.snapshot}'.")
        else:
            print(f"{args.snapshot}: {state}")

    elif args.lifecycle_cmd == "list":
        names = list_by_state(store, args.state)
        if not names:
            print(f"No snapshots with state '{args.state}'.")
        else:
            for name in names:
                print(name)

    elif args.lifecycle_cmd == "remove":
        removed = remove_lifecycle_state(store, args.snapshot)
        if removed:
            print(f"Lifecycle state removed for '{args.snapshot}'.")
        else:
            print(f"No lifecycle state found for '{args.snapshot}'.")


def build_lifecycle_parser(subparsers=None) -> argparse.ArgumentParser:
    desc = "Manage snapshot lifecycle states (draft, active, deprecated, archived)."
    if subparsers is not None:
        parser = subparsers.add_parser("lifecycle", help=desc)
    else:
        parser = argparse.ArgumentParser(prog="envforge lifecycle", description=desc)

    parser.add_argument("--store-dir", default=".envforge", dest="store_dir")
    sub = parser.add_subparsers(dest="lifecycle_cmd", required=True)

    p_set = sub.add_parser("set", help="Set lifecycle state for a snapshot.")
    p_set.add_argument("snapshot")
    p_set.add_argument("state", choices=VALID_STATES)

    p_get = sub.add_parser("get", help="Get lifecycle state of a snapshot.")
    p_get.add_argument("snapshot")

    p_list = sub.add_parser("list", help="List snapshots with a given lifecycle state.")
    p_list.add_argument("state", choices=VALID_STATES)

    p_rm = sub.add_parser("remove", help="Remove lifecycle state from a snapshot.")
    p_rm.add_argument("snapshot")

    parser.set_defaults(func=cmd_lifecycle)
    return parser
