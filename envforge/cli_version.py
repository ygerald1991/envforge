"""CLI commands for snapshot versioning."""

import argparse
from envforge.snapshot_version import (
    bump_version,
    get_version,
    set_version,
    reset_version,
    list_versions,
)


def cmd_version(args: argparse.Namespace) -> None:
    base_dir = args.base_dir

    if args.version_action == "bump":
        new_ver = bump_version(base_dir, args.snapshot)
        print(f"Bumped '{args.snapshot}' to version {new_ver}.")

    elif args.version_action == "get":
        ver = get_version(base_dir, args.snapshot)
        if ver is None:
            print(f"'{args.snapshot}' has no version set.")
        else:
            print(f"'{args.snapshot}' is at version {ver}.")

    elif args.version_action == "set":
        ver = set_version(base_dir, args.snapshot, args.number)
        print(f"Set '{args.snapshot}' to version {ver}.")

    elif args.version_action == "reset":
        reset_version(base_dir, args.snapshot)
        print(f"Version tracking removed for '{args.snapshot}'.")

    elif args.version_action == "list":
        versions = list_versions(base_dir)
        if not versions:
            print("No versioned snapshots found.")
        else:
            for name, ver in sorted(versions.items()):
                print(f"  {name}: v{ver}")


def build_version_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is not None:
        parser = subparsers.add_parser("version", help="Manage snapshot version numbers")
    else:
        parser = argparse.ArgumentParser(description="Manage snapshot version numbers")

    parser.add_argument("--base-dir", default=".envforge", help="Snapshot storage directory")
    sub = parser.add_subparsers(dest="version_action", required=True)

    bump_p = sub.add_parser("bump", help="Increment version for a snapshot")
    bump_p.add_argument("snapshot", help="Snapshot name")

    get_p = sub.add_parser("get", help="Get current version of a snapshot")
    get_p.add_argument("snapshot", help="Snapshot name")

    set_p = sub.add_parser("set", help="Set explicit version for a snapshot")
    set_p.add_argument("snapshot", help="Snapshot name")
    set_p.add_argument("number", type=int, help="Version number (>= 1)")

    reset_p = sub.add_parser("reset", help="Remove version tracking for a snapshot")
    reset_p.add_argument("snapshot", help="Snapshot name")

    sub.add_parser("list", help="List all versioned snapshots")

    parser.set_defaults(func=cmd_version)
    return parser
