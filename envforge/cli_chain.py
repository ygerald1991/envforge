"""CLI commands for snapshot chaining."""

from __future__ import annotations

import argparse
from typing import Any

from envforge.snapshot_chain import (
    get_ancestors,
    get_children,
    get_parent,
    remove_from_chain,
    set_parent,
)


def cmd_chain(args: Any) -> None:
    sub = args.chain_sub

    if sub == "set-parent":
        set_parent(args.store_dir, args.snapshot, args.parent)
        print(f"[chain] '{args.snapshot}' → parent '{args.parent}'")

    elif sub == "parent":
        parent = get_parent(args.store_dir, args.snapshot)
        if parent:
            print(parent)
        else:
            print(f"No parent recorded for '{args.snapshot}'.")

    elif sub == "ancestors":
        ancestors = get_ancestors(args.store_dir, args.snapshot)
        if not ancestors:
            print(f"No ancestors found for '{args.snapshot}'.")
        else:
            for a in ancestors:
                print(a)

    elif sub == "children":
        children = get_children(args.store_dir, args.snapshot)
        if not children:
            print(f"No children found for '{args.snapshot}'.")
        else:
            for c in children:
                print(c)

    elif sub == "remove":
        removed = remove_from_chain(args.store_dir, args.snapshot)
        if removed:
            print(f"[chain] Removed '{args.snapshot}' from chain index.")
        else:
            print(f"'{args.snapshot}' was not in the chain index.")


def build_chain_parser(subparsers: Any) -> argparse.ArgumentParser:
    p = subparsers.add_parser("chain", help="Manage snapshot parent/child chains")
    p.add_argument("--store-dir", default=".envforge", dest="store_dir")
    sub = p.add_subparsers(dest="chain_sub", required=True)

    sp = sub.add_parser("set-parent", help="Link snapshot to a parent")
    sp.add_argument("snapshot")
    sp.add_argument("parent")

    gp = sub.add_parser("parent", help="Show direct parent of a snapshot")
    gp.add_argument("snapshot")

    anc = sub.add_parser("ancestors", help="List all ancestors of a snapshot")
    anc.add_argument("snapshot")

    ch = sub.add_parser("children", help="List direct children of a snapshot")
    ch.add_argument("snapshot")

    rm = sub.add_parser("remove", help="Remove snapshot from chain index")
    rm.add_argument("snapshot")

    p.set_defaults(func=cmd_chain)
    return p
