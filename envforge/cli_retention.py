"""CLI commands for snapshot retention policies."""
from __future__ import annotations

import argparse

from envforge.snapshot_retention import (
    apply_retention_policy,
    get_retention_policy,
    list_retention_policies,
    remove_retention_policy,
    set_retention_policy,
)


def cmd_retention(args: argparse.Namespace) -> None:
    sub = args.retention_sub

    if sub == "set":
        policy = set_retention_policy(
            args.base_dir,
            args.name,
            max_count=args.max_count,
            max_age_days=args.max_age_days,
        )
        print(f"Retention policy '{policy['name']}' set (max_count={policy['max_count']}, max_age_days={policy['max_age_days']}).")

    elif sub == "get":
        policy = get_retention_policy(args.base_dir, args.name)
        if policy is None:
            print(f"No retention policy named '{args.name}'.")
        else:
            print(f"Policy: {policy['name']}")
            print(f"  max_count  : {policy['max_count']}")
            print(f"  max_age_days: {policy['max_age_days']}")
            print(f"  created_at : {policy['created_at']}")

    elif sub == "remove":
        removed = remove_retention_policy(args.base_dir, args.name)
        if removed:
            print(f"Retention policy '{args.name}' removed.")
        else:
            print(f"No retention policy named '{args.name}'.")

    elif sub == "list":
        policies = list_retention_policies(args.base_dir)
        if not policies:
            print("No retention policies defined.")
        else:
            for p in policies:
                age = p["max_age_days"] if p["max_age_days"] is not None else "unlimited"
                print(f"  {p['name']:20s}  max_count={p['max_count']}  max_age_days={age}")

    elif sub == "apply":
        import json
        from pathlib import Path

        snap_file = Path(args.snapshots_json)
        snapshots = json.loads(snap_file.read_text())
        to_prune = apply_retention_policy(args.base_dir, args.name, snapshots)
        if not to_prune:
            print("No snapshots to prune.")
        else:
            print(f"{len(to_prune)} snapshot(s) to prune:")
            for sname in to_prune:
                print(f"  - {sname}")


def build_retention_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser("retention", help="Manage snapshot retention policies")
    p.add_argument("--base-dir", dest="base_dir", default=".envforge", help="Storage directory")
    sub = p.add_subparsers(dest="retention_sub", required=True)

    s = sub.add_parser("set", help="Create or update a retention policy")
    s.add_argument("name", help="Policy name")
    s.add_argument("--max-count", dest="max_count", type=int, required=True, help="Maximum number of snapshots to keep")
    s.add_argument("--max-age-days", dest="max_age_days", type=int, default=None, help="Maximum age in days")

    g = sub.add_parser("get", help="Show a retention policy")
    g.add_argument("name", help="Policy name")

    r = sub.add_parser("remove", help="Delete a retention policy")
    r.add_argument("name", help="Policy name")

    sub.add_parser("list", help="List all retention policies")

    a = sub.add_parser("apply", help="Apply a policy to a list of snapshots (dry-run output)")
    a.add_argument("name", help="Policy name")
    a.add_argument("snapshots_json", help="Path to JSON file containing snapshot metadata list")

    p.set_defaults(func=cmd_retention)
    return p
