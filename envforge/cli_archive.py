"""CLI commands for snapshot archiving."""

import argparse
from pathlib import Path
from envforge.snapshot_archive import (
    archive_snapshot,
    list_archived_snapshots,
    extract_snapshot,
    delete_archive,
)

_DEFAULT_ARCHIVE_DIR = ".envforge/archives"


def cmd_archive(args: argparse.Namespace) -> None:
    sub = args.archive_sub

    if sub == "add":
        dest = archive_snapshot(
            snapshot_path=args.snapshot_path,
            archive_dir=args.archive_dir,
            archive_name=args.archive_name,
        )
        print(f"Archived '{args.snapshot_path}' → {dest}")

    elif sub == "list":
        names = list_archived_snapshots(
            archive_dir=args.archive_dir,
            archive_name=args.archive_name,
        )
        if not names:
            print(f"Archive '{args.archive_name}' is empty or does not exist.")
        else:
            for n in names:
                print(n)

    elif sub == "extract":
        out = extract_snapshot(
            archive_dir=args.archive_dir,
            archive_name=args.archive_name,
            snapshot_name=args.snapshot_name,
            dest_dir=args.dest_dir,
        )
        print(f"Extracted '{args.snapshot_name}' → {out}")

    elif sub == "delete":
        removed = delete_archive(
            archive_dir=args.archive_dir,
            archive_name=args.archive_name,
        )
        if removed:
            print(f"Deleted archive '{args.archive_name}'.")
        else:
            print(f"Archive '{args.archive_name}' not found.")


def build_archive_parser(parent: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = parent.add_parser("archive", help="Manage snapshot archives")
    p.add_argument("--archive-dir", default=_DEFAULT_ARCHIVE_DIR)
    sub = p.add_subparsers(dest="archive_sub", required=True)

    add_p = sub.add_parser("add", help="Add a snapshot to an archive")
    add_p.add_argument("archive_name")
    add_p.add_argument("snapshot_path")

    lst_p = sub.add_parser("list", help="List snapshots in an archive")
    lst_p.add_argument("archive_name")

    ext_p = sub.add_parser("extract", help="Extract a snapshot from an archive")
    ext_p.add_argument("archive_name")
    ext_p.add_argument("snapshot_name")
    ext_p.add_argument("dest_dir")

    del_p = sub.add_parser("delete", help="Delete an entire archive")
    del_p.add_argument("archive_name")

    p.set_defaults(func=cmd_archive)
    return p
