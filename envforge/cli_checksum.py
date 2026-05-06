"""CLI commands for snapshot checksum management."""

import argparse

from envforge.snapshot_checksum import (
    store_checksum,
    get_checksum,
    verify_checksum,
    remove_checksum,
    list_checksums,
)
from envforge.core import load_snapshot


def cmd_checksum(args: argparse.Namespace) -> None:
    sub = args.checksum_cmd

    if sub == "store":
        variables = load_snapshot(args.store_dir, args.snapshot)
        digest = store_checksum(args.store_dir, args.snapshot, variables)
        print(f"Stored checksum for '{args.snapshot}': {digest}")

    elif sub == "get":
        digest = get_checksum(args.store_dir, args.snapshot)
        if digest is None:
            print(f"No checksum found for '{args.snapshot}'.")
        else:
            print(f"{args.snapshot}: {digest}")

    elif sub == "verify":
        variables = load_snapshot(args.store_dir, args.snapshot)
        ok = verify_checksum(args.store_dir, args.snapshot, variables)
        if ok:
            print(f"'{args.snapshot}' checksum OK.")
        else:
            print(f"'{args.snapshot}' checksum MISMATCH or not stored.")

    elif sub == "remove":
        removed = remove_checksum(args.store_dir, args.snapshot)
        if removed:
            print(f"Removed checksum for '{args.snapshot}'.")
        else:
            print(f"No checksum entry found for '{args.snapshot}'.")

    elif sub == "list":
        entries = list_checksums(args.store_dir)
        if not entries:
            print("No checksums stored.")
        else:
            for name, digest in sorted(entries.items()):
                print(f"{name}: {digest}")


def build_checksum_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is None:
        parser = argparse.ArgumentParser(description="Manage snapshot checksums")
        sub = parser.add_subparsers(dest="checksum_cmd")
    else:
        parser = subparsers.add_parser("checksum", help="Manage snapshot checksums")
        sub = parser.add_subparsers(dest="checksum_cmd")

    for cmd in ("store", "get", "verify", "remove"):
        p = sub.add_parser(cmd)
        p.add_argument("snapshot", help="Snapshot name")
        p.add_argument("--store-dir", default=".envforge", dest="store_dir")

    p_list = sub.add_parser("list")
    p_list.add_argument("--store-dir", default=".envforge", dest="store_dir")

    return parser
