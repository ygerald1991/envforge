"""CLI commands for snapshot bookmarks."""

import argparse
from envforge.snapshot_bookmark import (
    set_bookmark,
    remove_bookmark,
    resolve_bookmark,
    list_bookmarks,
    bookmarks_for_snapshot,
)


def cmd_bookmark(args: argparse.Namespace) -> None:
    base_dir = args.dir

    if args.bookmark_cmd == "set":
        set_bookmark(base_dir, args.bookmark, args.snapshot)
        print(f"Bookmark '{args.bookmark}' -> '{args.snapshot}'")

    elif args.bookmark_cmd == "remove":
        removed = remove_bookmark(base_dir, args.bookmark)
        if removed:
            print(f"Removed bookmark '{args.bookmark}'")
        else:
            print(f"Bookmark '{args.bookmark}' not found")

    elif args.bookmark_cmd == "resolve":
        snapshot = resolve_bookmark(base_dir, args.bookmark)
        if snapshot:
            print(snapshot)
        else:
            print(f"No bookmark named '{args.bookmark}'")

    elif args.bookmark_cmd == "list":
        data = list_bookmarks(base_dir)
        if not data:
            print("No bookmarks defined.")
        else:
            for bm, sn in sorted(data.items()):
                print(f"  {bm} -> {sn}")

    elif args.bookmark_cmd == "for-snapshot":
        bms = bookmarks_for_snapshot(base_dir, args.snapshot)
        if not bms:
            print(f"No bookmarks for snapshot '{args.snapshot}'")
        else:
            for bm in sorted(bms):
                print(f"  {bm}")


def build_bookmark_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is None:
        parser = argparse.ArgumentParser(prog="envforge bookmark")
        sub = parser.add_subparsers(dest="bookmark_cmd")
    else:
        parser = subparsers.add_parser("bookmark", help="Manage snapshot bookmarks")
        sub = parser.add_subparsers(dest="bookmark_cmd")

    p_set = sub.add_parser("set", help="Set a bookmark")
    p_set.add_argument("bookmark")
    p_set.add_argument("snapshot")

    p_rm = sub.add_parser("remove", help="Remove a bookmark")
    p_rm.add_argument("bookmark")

    p_res = sub.add_parser("resolve", help="Resolve a bookmark to a snapshot name")
    p_res.add_argument("bookmark")

    sub.add_parser("list", help="List all bookmarks")

    p_for = sub.add_parser("for-snapshot", help="List bookmarks pointing to a snapshot")
    p_for.add_argument("snapshot")

    parser.set_defaults(func=cmd_bookmark)
    return parser
