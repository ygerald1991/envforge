"""CLI commands for snapshot label management."""

from __future__ import annotations

import argparse
from envforge.snapshot_labels import (
    set_label,
    remove_label,
    get_labels,
    find_by_label,
)

_DEFAULT_STORE = ".envforge"


def cmd_labels(args: argparse.Namespace) -> None:
    store = getattr(args, "store", _DEFAULT_STORE)

    if args.labels_cmd == "set":
        set_label(store, args.snapshot, args.key, args.value)
        print(f"Label '{args.key}={args.value}' set on '{args.snapshot}'.")

    elif args.labels_cmd == "remove":
        removed = remove_label(store, args.snapshot, args.key)
        if removed:
            print(f"Label '{args.key}' removed from '{args.snapshot}'.")
        else:
            print(f"Label '{args.key}' not found on '{args.snapshot}'.")

    elif args.labels_cmd == "list":
        labels = get_labels(store, args.snapshot)
        if not labels:
            print(f"No labels for '{args.snapshot}'.")
        else:
            for k, v in sorted(labels.items()):
                print(f"  {k}={v}")

    elif args.labels_cmd == "find":
        value = getattr(args, "value", None)
        matches = find_by_label(store, args.key, value)
        if not matches:
            print("No snapshots matched.")
        else:
            for name in matches:
                print(f"  {name}")


def build_labels_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("labels", help="Manage snapshot labels")
    sub = p.add_subparsers(dest="labels_cmd", required=True)

    # set
    ps = sub.add_parser("set", help="Set a label on a snapshot")
    ps.add_argument("snapshot")
    ps.add_argument("key")
    ps.add_argument("value")

    # remove
    pr = sub.add_parser("remove", help="Remove a label from a snapshot")
    pr.add_argument("snapshot")
    pr.add_argument("key")

    # list
    pl = sub.add_parser("list", help="List labels for a snapshot")
    pl.add_argument("snapshot")

    # find
    pf = sub.add_parser("find", help="Find snapshots by label key (and optional value)")
    pf.add_argument("key")
    pf.add_argument("value", nargs="?", default=None)

    p.set_defaults(func=cmd_labels)
