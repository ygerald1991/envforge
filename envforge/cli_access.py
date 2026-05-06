"""CLI commands for snapshot access log."""

import argparse
import os

from envforge.snapshot_access import get_access_log, get_last_accessed, format_access_log


def cmd_access(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "base_dir", None) or os.environ.get("ENVFORGE_DIR", ".envforge")

    if args.access_cmd == "log":
        entries = get_access_log(base_dir, snapshot_name=getattr(args, "snapshot", None))
        print(format_access_log(entries))

    elif args.access_cmd == "last":
        if not args.snapshot:
            print("Error: snapshot name required for 'last' subcommand.")
            return
        entry = get_last_accessed(base_dir, args.snapshot)
        if entry is None:
            print(f"No access records for snapshot '{args.snapshot}'.")
        else:
            print(format_access_log([entry]))

    else:
        print(f"Unknown access subcommand: {args.access_cmd}")


def build_access_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is not None:
        parser = subparsers.add_parser("access", help="View snapshot access log")
    else:
        parser = argparse.ArgumentParser(prog="envforge access", description="View snapshot access log")

    sub = parser.add_subparsers(dest="access_cmd")
    sub.required = True

    log_p = sub.add_parser("log", help="Show access log")
    log_p.add_argument("snapshot", nargs="?", default=None, help="Filter by snapshot name")

    last_p = sub.add_parser("last", help="Show last access for a snapshot")
    last_p.add_argument("snapshot", help="Snapshot name")

    parser.set_defaults(func=cmd_access)
    return parser
