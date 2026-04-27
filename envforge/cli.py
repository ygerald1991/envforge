"""Command-line interface for envforge."""

import sys
import argparse
from envforge.core import capture_env, save_snapshot, list_snapshots
from envforge.diff import diff_snapshots, format_diff
from envforge.restore import restore_to_env, restore_to_shell_script, selective_restore

DEFAULT_DIR = ".envforge"


def cmd_capture(args):
    env = capture_env()
    save_snapshot(args.name, env, args.dir)
    print(f"Snapshot '{args.name}' saved ({len(env)} variables).")


def cmd_list(args):
    snapshots = list_snapshots(args.dir)
    if not snapshots:
        print("No snapshots found.")
    else:
        for name in snapshots:
            print(f"  {name}")


def cmd_diff(args):
    result = diff_snapshots(args.snap1, args.snap2, args.dir)
    print(format_diff(result))


def cmd_restore(args):
    if args.shell:
        script = restore_to_shell_script(
            args.name,
            snapshots_dir=args.dir,
            shell=args.shell,
            output_path=args.output,
        )
        if not args.output:
            print(script)
        else:
            print(f"Script written to {args.output}")
    elif args.keys:
        applied = selective_restore(args.name, args.keys, args.dir)
        print(f"Restored {len(applied)} variable(s) from '{args.name}':")
        for k in sorted(applied):
            print(f"  {k}={applied[k]}")
    else:
        applied = restore_to_env(args.name, args.dir)
        print(f"Restored {len(applied)} variable(s) from '{args.name}' into current process.")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envforge",
        description="Snapshot, diff, and restore environment variable sets.",
    )
    parser.add_argument("--dir", default=DEFAULT_DIR, help="Snapshots directory.")
    sub = parser.add_subparsers(dest="command", required=True)

    # capture
    p_capture = sub.add_parser("capture", help="Capture current environment as a snapshot.")
    p_capture.add_argument("name", help="Snapshot name.")
    p_capture.set_defaults(func=cmd_capture)

    # list
    p_list = sub.add_parser("list", help="List available snapshots.")
    p_list.set_defaults(func=cmd_list)

    # diff
    p_diff = sub.add_parser("diff", help="Diff two snapshots.")
    p_diff.add_argument("snap1", help="First snapshot name.")
    p_diff.add_argument("snap2", help="Second snapshot name.")
    p_diff.set_defaults(func=cmd_diff)

    # restore
    p_restore = sub.add_parser("restore", help="Restore a snapshot.")
    p_restore.add_argument("name", help="Snapshot name to restore.")
    p_restore.add_argument("--shell", choices=["bash", "sh", "fish"], help="Emit a shell script.")
    p_restore.add_argument("--output", help="Write shell script to this file.")
    p_restore.add_argument("--keys", nargs="+", help="Restore only specific keys.")
    p_restore.set_defaults(func=cmd_restore)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
