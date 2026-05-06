"""CLI commands for snapshot comment management."""

import argparse
from envforge.snapshot_comment import (
    add_comment,
    get_comments,
    delete_comment,
    clear_comments,
    format_comments,
)


def cmd_comment(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "base_dir", ".")

    if args.comment_action == "add":
        entry = add_comment(base_dir, args.snapshot, args.author, args.text)
        print(f"Comment added to '{args.snapshot}' at {entry['timestamp']}")

    elif args.comment_action == "list":
        comments = get_comments(base_dir, args.snapshot)
        print(f"Comments for '{args.snapshot}':")
        print(format_comments(comments))

    elif args.comment_action == "delete":
        ok = delete_comment(base_dir, args.snapshot, args.index)
        if ok:
            print(f"Comment [{args.index}] removed from '{args.snapshot}'.")
        else:
            print(f"No comment at index {args.index} for '{args.snapshot}'.")

    elif args.comment_action == "clear":
        count = clear_comments(base_dir, args.snapshot)
        print(f"Cleared {count} comment(s) from '{args.snapshot}'.")

    else:
        print(f"Unknown comment action: {args.comment_action}")


def build_comment_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is not None:
        p = subparsers.add_parser("comment", help="Manage snapshot comments")
    else:
        p = argparse.ArgumentParser(description="Manage snapshot comments")

    sub = p.add_subparsers(dest="comment_action", required=True)

    add_p = sub.add_parser("add", help="Add a comment")
    add_p.add_argument("snapshot", help="Snapshot name")
    add_p.add_argument("author", help="Comment author")
    add_p.add_argument("text", help="Comment text")

    list_p = sub.add_parser("list", help="List comments")
    list_p.add_argument("snapshot", help="Snapshot name")

    del_p = sub.add_parser("delete", help="Delete a comment by index")
    del_p.add_argument("snapshot", help="Snapshot name")
    del_p.add_argument("index", type=int, help="Comment index")

    clr_p = sub.add_parser("clear", help="Clear all comments for a snapshot")
    clr_p.add_argument("snapshot", help="Snapshot name")

    p.set_defaults(func=cmd_comment)
    return p
