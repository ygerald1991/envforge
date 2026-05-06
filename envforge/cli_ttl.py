"""CLI commands for snapshot TTL management."""

import argparse
from datetime import timezone

from envforge.snapshot_ttl import (
    set_ttl,
    remove_ttl,
    get_ttl,
    get_expired_snapshots,
)


def cmd_ttl(args, store_dir: str = ".envforge") -> None:
    sub = args.ttl_command

    if sub == "set":
        expires_at = set_ttl(store_dir, args.snapshot, args.seconds)
        print(
            f"TTL set for '{args.snapshot}': expires at "
            f"{expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )

    elif sub == "remove":
        removed = remove_ttl(store_dir, args.snapshot)
        if removed:
            print(f"TTL removed for '{args.snapshot}'.")
        else:
            print(f"No TTL found for '{args.snapshot}'.")

    elif sub == "show":
        expiry = get_ttl(store_dir, args.snapshot)
        if expiry is None:
            print(f"No TTL set for '{args.snapshot}'.")
        else:
            from envforge.snapshot_ttl import is_expired
            status = "EXPIRED" if is_expired(store_dir, args.snapshot) else "active"
            print(
                f"'{args.snapshot}' expires at "
                f"{expiry.strftime('%Y-%m-%d %H:%M:%S UTC')} [{status}]"
            )

    elif sub == "list-expired":
        expired = get_expired_snapshots(store_dir)
        if not expired:
            print("No expired snapshots.")
        else:
            print("Expired snapshots:")
            for name in expired:
                print(f"  {name}")

    else:
        print(f"Unknown ttl subcommand: {sub}")


def build_ttl_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is None:
        parser = argparse.ArgumentParser(description="Manage snapshot TTLs")
        sub = parser.add_subparsers(dest="ttl_command")
    else:
        parser = subparsers.add_parser("ttl", help="Manage snapshot TTLs")
        sub = parser.add_subparsers(dest="ttl_command")

    p_set = sub.add_parser("set", help="Set a TTL on a snapshot")
    p_set.add_argument("snapshot", help="Snapshot name")
    p_set.add_argument("seconds", type=int, help="TTL in seconds")

    p_rm = sub.add_parser("remove", help="Remove TTL from a snapshot")
    p_rm.add_argument("snapshot", help="Snapshot name")

    p_show = sub.add_parser("show", help="Show TTL for a snapshot")
    p_show.add_argument("snapshot", help="Snapshot name")

    sub.add_parser("list-expired", help="List all expired snapshots")

    return parser
