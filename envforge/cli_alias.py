"""CLI commands for snapshot alias management."""

from __future__ import annotations

import argparse
from typing import Any

from envforge import alias as _alias


def cmd_alias(args: Any) -> None:
    sub = args.alias_sub

    if sub == "set":
        _alias.set_alias(args.snapshot_dir, args.alias, args.snapshot)
        print(f"Alias '{args.alias}' -> '{args.snapshot}' saved.")

    elif sub == "remove":
        removed = _alias.remove_alias(args.snapshot_dir, args.alias)
        if removed:
            print(f"Alias '{args.alias}' removed.")
        else:
            print(f"Alias '{args.alias}' not found.")

    elif sub == "resolve":
        name = _alias.resolve_alias(args.snapshot_dir, args.alias)
        if name:
            print(name)
        else:
            print(f"No alias named '{args.alias}'.")

    elif sub == "list":
        mapping = _alias.list_aliases(args.snapshot_dir)
        if not mapping:
            print("No aliases defined.")
        else:
            for a, snap in sorted(mapping.items()):
                print(f"{a:30s} -> {snap}")

    elif sub == "lookup":
        aliases = _alias.get_aliases_for_snapshot(args.snapshot_dir, args.snapshot)
        if aliases:
            print("\n".join(sorted(aliases)))
        else:
            print(f"No aliases point to '{args.snapshot}'.")


def build_alias_parser(subparsers: Any) -> argparse.ArgumentParser:
    p = subparsers.add_parser("alias", help="Manage snapshot aliases")
    p.add_argument("--snapshot-dir", default=".envforge", metavar="DIR")
    sub = p.add_subparsers(dest="alias_sub", required=True)

    s = sub.add_parser("set", help="Assign an alias to a snapshot")
    s.add_argument("alias")
    s.add_argument("snapshot")

    r = sub.add_parser("remove", help="Remove an alias")
    r.add_argument("alias")

    v = sub.add_parser("resolve", help="Resolve an alias to a snapshot name")
    v.add_argument("alias")

    sub.add_parser("list", help="List all aliases")

    lk = sub.add_parser("lookup", help="Find aliases for a snapshot")
    lk.add_argument("snapshot")

    p.set_defaults(func=cmd_alias)
    return p
