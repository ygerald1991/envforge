"""CLI commands for snapshot namespace management."""

from __future__ import annotations

import argparse
from typing import Optional

from envforge.snapshot_namespace import (
    add_to_namespace,
    remove_from_namespace,
    get_namespace,
    list_namespaces,
    delete_namespace,
)

DEFAULT_DIR = ".envforge"


def cmd_namespace(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "dir", DEFAULT_DIR)

    if args.namespace_cmd == "add":
        add_to_namespace(base_dir, args.namespace, args.snapshot)
        print(f"Added '{args.snapshot}' to namespace '{args.namespace}'.")

    elif args.namespace_cmd == "remove":
        removed = remove_from_namespace(base_dir, args.namespace, args.snapshot)
        if removed:
            print(f"Removed '{args.snapshot}' from namespace '{args.namespace}'.")
        else:
            print(f"'{args.snapshot}' not found in namespace '{args.namespace}'.")

    elif args.namespace_cmd == "list":
        if args.namespace:
            members = get_namespace(base_dir, args.namespace)
            if members is None:
                print(f"Namespace '{args.namespace}' does not exist.")
            elif not members:
                print(f"Namespace '{args.namespace}' is empty.")
            else:
                for name in members:
                    print(name)
        else:
            namespaces = list_namespaces(base_dir)
            if not namespaces:
                print("No namespaces defined.")
            else:
                for ns in namespaces:
                    print(ns)

    elif args.namespace_cmd == "delete":
        deleted = delete_namespace(base_dir, args.namespace)
        if deleted:
            print(f"Namespace '{args.namespace}' deleted.")
        else:
            print(f"Namespace '{args.namespace}' does not exist.")


def build_namespace_parser(subparsers: Optional[argparse._SubParsersAction] = None):
    if subparsers is None:
        parser = argparse.ArgumentParser(description="Manage snapshot namespaces")
        sub = parser.add_subparsers(dest="namespace_cmd")
    else:
        parser = subparsers.add_parser("namespace", help="Manage snapshot namespaces")
        sub = parser.add_subparsers(dest="namespace_cmd")

    add_p = sub.add_parser("add", help="Add snapshot to a namespace")
    add_p.add_argument("namespace")
    add_p.add_argument("snapshot")

    rem_p = sub.add_parser("remove", help="Remove snapshot from a namespace")
    rem_p.add_argument("namespace")
    rem_p.add_argument("snapshot")

    lst_p = sub.add_parser("list", help="List namespaces or members of a namespace")
    lst_p.add_argument("namespace", nargs="?", default=None)

    del_p = sub.add_parser("delete", help="Delete an entire namespace")
    del_p.add_argument("namespace")

    parser.set_defaults(func=cmd_namespace)
    return parser
