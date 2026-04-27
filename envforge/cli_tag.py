"""CLI commands for snapshot tagging."""

import argparse
import sys

from envforge.tag import (
    add_tag,
    list_tags,
    remove_tag,
    snapshots_for_tag,
    tags_for_snapshot,
)

DEFAULT_SNAPSHOT_DIR = ".envforge_snapshots"


def cmd_tag(args: argparse.Namespace) -> None:
    """Dispatch tag subcommands."""
    snapshot_dir = getattr(args, "snapshot_dir", DEFAULT_SNAPSHOT_DIR)

    if args.tag_action == "add":
        add_tag(args.snapshot, args.tag, snapshot_dir)
        print(f"Tagged '{args.snapshot}' with '{args.tag}'.")

    elif args.tag_action == "remove":
        removed = remove_tag(args.snapshot, args.tag, snapshot_dir)
        if removed:
            print(f"Removed tag '{args.tag}' from '{args.snapshot}'.")
        else:
            print(f"Tag '{args.tag}' not found on '{args.snapshot}'.")
            sys.exit(1)

    elif args.tag_action == "list":
        index = list_tags(snapshot_dir)
        if not index:
            print("No tags defined.")
            return
        for tag, snapshots in sorted(index.items()):
            print(f"{tag}: {', '.join(snapshots)}")

    elif args.tag_action == "find":
        snaps = snapshots_for_tag(args.tag, snapshot_dir)
        if not snaps:
            print(f"No snapshots tagged '{args.tag}'.")
        else:
            for s in snaps:
                print(s)

    elif args.tag_action == "show":
        tags = tags_for_snapshot(args.snapshot, snapshot_dir)
        if not tags:
            print(f"No tags on snapshot '{args.snapshot}'.")
        else:
            print(", ".join(sorted(tags)))


def build_tag_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register 'tag' command and its subcommands."""
    tag_parser = subparsers.add_parser("tag", help="Manage snapshot tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_action", required=True)

    p_add = tag_sub.add_parser("add", help="Add a tag to a snapshot")
    p_add.add_argument("snapshot", help="Snapshot name")
    p_add.add_argument("tag", help="Tag label")

    p_rm = tag_sub.add_parser("remove", help="Remove a tag from a snapshot")
    p_rm.add_argument("snapshot", help="Snapshot name")
    p_rm.add_argument("tag", help="Tag label")

    tag_sub.add_parser("list", help="List all tags")

    p_find = tag_sub.add_parser("find", help="Find snapshots by tag")
    p_find.add_argument("tag", help="Tag label to search for")

    p_show = tag_sub.add_parser("show", help="Show tags for a snapshot")
    p_show.add_argument("snapshot", help="Snapshot name")

    tag_parser.set_defaults(func=cmd_tag)
