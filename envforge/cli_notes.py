"""CLI commands for managing snapshot notes."""

import argparse
from envforge.snapshot_notes import (
    set_note,
    get_note,
    remove_note,
    list_notes,
    format_notes,
)


def cmd_notes(args: argparse.Namespace) -> None:
    snapshot_dir = args.snapshot_dir

    if args.notes_action == "set":
        set_note(snapshot_dir, args.snapshot, args.note)
        print(f"Note set for snapshot '{args.snapshot}'.")

    elif args.notes_action == "get":
        note = get_note(snapshot_dir, args.snapshot)
        if note is None:
            print(f"No note found for snapshot '{args.snapshot}'.")
        else:
            print(f"{args.snapshot}: {note}")

    elif args.notes_action == "remove":
        removed = remove_note(snapshot_dir, args.snapshot)
        if removed:
            print(f"Note removed for snapshot '{args.snapshot}'.")
        else:
            print(f"No note found for snapshot '{args.snapshot}'.")

    elif args.notes_action == "list":
        notes = list_notes(snapshot_dir)
        print(format_notes(notes))

    else:
        print(f"Unknown notes action: {args.notes_action}")


def build_notes_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("notes", help="Manage notes attached to snapshots")
    p.add_argument(
        "--snapshot-dir", default=".envforge", dest="snapshot_dir",
        help="Directory where snapshots are stored",
    )
    sub = p.add_subparsers(dest="notes_action", required=True)

    p_set = sub.add_parser("set", help="Attach a note to a snapshot")
    p_set.add_argument("snapshot", help="Snapshot name")
    p_set.add_argument("note", help="Note text")

    p_get = sub.add_parser("get", help="Retrieve the note for a snapshot")
    p_get.add_argument("snapshot", help="Snapshot name")

    p_rm = sub.add_parser("remove", help="Remove the note from a snapshot")
    p_rm.add_argument("snapshot", help="Snapshot name")

    sub.add_parser("list", help="List all snapshot notes")

    p.set_defaults(func=cmd_notes)
