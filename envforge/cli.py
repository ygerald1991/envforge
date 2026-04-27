"""CLI entry point for envforge."""

import argparse
import os
import sys

from envforge.core import capture_env, save_snapshot, list_snapshots
from envforge.diff import diff_snapshots, format_diff
from envforge.restore import restore_to_shell_script, selective_restore
from envforge.export import export_snapshot, EXPORT_FORMATS

DEFAULT_SNAPSHOT_DIR = os.path.expanduser("~/.envforge/snapshots")


def cmd_capture(args):
    env = capture_env()
    path = save_snapshot(args.name, env, args.snapshot_dir)
    print(f"Snapshot '{args.name}' saved to {path}")


def cmd_list(args):
    snapshots = list_snapshots(args.snapshot_dir)
    if not snapshots:
        print("No snapshots found.")
    else:
        for name in snapshots:
            print(name)


def cmd_diff(args):
    result = diff_snapshots(args.snap_a, args.snap_b, args.snapshot_dir)
    print(format_diff(result))


def cmd_restore(args):
    keys = args.keys if args.keys else None
    script = selective_restore(args.name, args.snapshot_dir, keys) if keys else restore_to_shell_script(args.name, args.snapshot_dir)
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(script)
        print(f"Restore script written to {args.output}")
    else:
        print(script)


def cmd_export(args):
    content = export_snapshot(
        args.name,
        args.snapshot_dir,
        fmt=args.format,
        output_path=args.output if args.output else None,
    )
    if args.output:
        print(f"Exported '{args.name}' as {args.format} to {args.output}")
    else:
        print(content, end="")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envforge",
        description="Snapshot, diff, and restore environment variable sets.",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=DEFAULT_SNAPSHOT_DIR,
        help="Directory where snapshots are stored.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # capture
    p_capture = sub.add_parser("capture", help="Capture current environment as a snapshot.")
    p_capture.add_argument("name", help="Name for the snapshot.")
    p_capture.set_defaults(func=cmd_capture)

    # list
    p_list = sub.add_parser("list", help="List all saved snapshots.")
    p_list.set_defaults(func=cmd_list)

    # diff
    p_diff = sub.add_parser("diff", help="Diff two snapshots.")
    p_diff.add_argument("snap_a", help="First snapshot name.")
    p_diff.add_argument("snap_b", help="Second snapshot name.")
    p_diff.set_defaults(func=cmd_diff)

    # restore
    p_restore = sub.add_parser("restore", help="Restore a snapshot to a shell script.")
    p_restore.add_argument("name", help="Snapshot name to restore.")
    p_restore.add_argument("--keys", nargs="+", help="Restore only specific keys.")
    p_restore.add_argument("--output", help="Write script to this file instead of stdout.")
    p_restore.set_defaults(func=cmd_restore)

    # export
    p_export = sub.add_parser("export", help="Export a snapshot to dotenv, JSON, or shell format.")
    p_export.add_argument("name", help="Snapshot name to export.")
    p_export.add_argument(
        "--format", choices=list(EXPORT_FORMATS.keys()), default="dotenv",
        help="Output format (default: dotenv).",
    )
    p_export.add_argument("--output", help="Write output to this file instead of stdout.")
    p_export.set_defaults(func=cmd_export)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
