"""CLI commands for snapshot group management."""

import argparse
from envforge.snapshot_group import (
    create_group,
    add_to_group,
    remove_from_group,
    delete_group,
    get_group,
    list_groups,
)

_DEFAULT_DIR = ".envforge"


def cmd_group(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "base_dir", _DEFAULT_DIR)

    if args.group_action == "create":
        create_group(base_dir, args.name, args.snapshots)
        print(f"Group '{args.name}' created with {len(args.snapshots)} snapshot(s).")

    elif args.group_action == "add":
        add_to_group(base_dir, args.name, args.snapshot)
        print(f"Snapshot '{args.snapshot}' added to group '{args.name}'.")

    elif args.group_action == "remove":
        removed = remove_from_group(base_dir, args.name, args.snapshot)
        if removed:
            print(f"Snapshot '{args.snapshot}' removed from group '{args.name}'.")
        else:
            print(f"Snapshot '{args.snapshot}' was not in group '{args.name}'.")

    elif args.group_action == "delete":
        deleted = delete_group(base_dir, args.name)
        if deleted:
            print(f"Group '{args.name}' deleted.")
        else:
            print(f"Group '{args.name}' not found.")

    elif args.group_action == "show":
        members = get_group(base_dir, args.name)
        if members is None:
            print(f"Group '{args.name}' not found.")
        elif not members:
            print(f"Group '{args.name}' is empty.")
        else:
            print(f"Group '{args.name}':")
            for m in members:
                print(f"  - {m}")

    elif args.group_action == "list":
        groups = list_groups(base_dir)
        if not groups:
            print("No groups defined.")
        else:
            for name, members in groups.items():
                print(f"{name} ({len(members)} snapshot(s)): {', '.join(members)}")


def build_group_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is not None:
        parser = subparsers.add_parser("group", help="Manage snapshot groups")
    else:
        parser = argparse.ArgumentParser(prog="envforge group")

    sub = parser.add_subparsers(dest="group_action", required=True)

    p_create = sub.add_parser("create", help="Create a new group")
    p_create.add_argument("name", help="Group name")
    p_create.add_argument("snapshots", nargs="+", help="Snapshot names")

    p_add = sub.add_parser("add", help="Add a snapshot to a group")
    p_add.add_argument("name", help="Group name")
    p_add.add_argument("snapshot", help="Snapshot name")

    p_remove = sub.add_parser("remove", help="Remove a snapshot from a group")
    p_remove.add_argument("name", help="Group name")
    p_remove.add_argument("snapshot", help="Snapshot name")

    p_delete = sub.add_parser("delete", help="Delete a group")
    p_delete.add_argument("name", help="Group name")

    p_show = sub.add_parser("show", help="Show members of a group")
    p_show.add_argument("name", help="Group name")

    sub.add_parser("list", help="List all groups")

    parser.set_defaults(func=cmd_group)
    return parser
