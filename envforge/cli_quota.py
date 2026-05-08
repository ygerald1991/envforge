"""CLI commands for snapshot quota management."""

from __future__ import annotations

import argparse
from typing import Optional

from envforge.snapshot_quota import (
    set_quota,
    get_quota,
    remove_quota,
    list_quotas,
    check_quota,
)


def cmd_quota(args: argparse.Namespace) -> None:
    store = args.store_dir

    if args.quota_action == "set":
        ns: Optional[str] = getattr(args, "namespace", None) or None
        entry = set_quota(store, args.limit, namespace=ns)
        scope = ns or "global"
        print(f"Quota set: {scope} → {entry['limit']} snapshots")

    elif args.quota_action == "get":
        ns = getattr(args, "namespace", None) or None
        entry = get_quota(store, namespace=ns)
        if entry is None:
            scope = ns or "global"
            print(f"No quota set for {scope}.")
        else:
            print(f"Quota [{entry['namespace']}]: {entry['limit']} snapshots")

    elif args.quota_action == "remove":
        ns = getattr(args, "namespace", None) or None
        removed = remove_quota(store, namespace=ns)
        scope = ns or "global"
        if removed:
            print(f"Quota removed for {scope}.")
        else:
            print(f"No quota found for {scope}.")

    elif args.quota_action == "list":
        entries = list_quotas(store)
        if not entries:
            print("No quotas defined.")
        else:
            for e in entries:
                print(f"  [{e['namespace']}]: {e['limit']} snapshots")

    elif args.quota_action == "check":
        ns = getattr(args, "namespace", None) or None
        ok = check_quota(store, args.count, namespace=ns)
        scope = ns or "global"
        status = "within quota" if ok else "EXCEEDS quota"
        print(f"Count {args.count} is {status} for {scope}.")


def build_quota_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("quota", help="Manage snapshot quotas")
    p.add_argument("--store-dir", default=".envforge", dest="store_dir")
    sub = p.add_subparsers(dest="quota_action", required=True)

    s = sub.add_parser("set", help="Set a quota limit")
    s.add_argument("limit", type=int, help="Maximum number of snapshots")
    s.add_argument("--namespace", default=None)

    g = sub.add_parser("get", help="Get quota for a namespace")
    g.add_argument("--namespace", default=None)

    r = sub.add_parser("remove", help="Remove a quota")
    r.add_argument("--namespace", default=None)

    sub.add_parser("list", help="List all quotas")

    ck = sub.add_parser("check", help="Check whether a count is within quota")
    ck.add_argument("count", type=int, help="Current snapshot count")
    ck.add_argument("--namespace", default=None)

    p.set_defaults(func=cmd_quota)
