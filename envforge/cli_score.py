"""CLI commands for snapshot scoring."""

from __future__ import annotations

import argparse

from envforge.snapshot_score import (
    get_score,
    rank_snapshots,
    remove_score,
    set_score,
)


def cmd_score(args: argparse.Namespace) -> None:
    sub = args.score_cmd

    if sub == "set":
        score = set_score(args.store_dir, args.snapshot, args.score)
        print(f"Score for '{args.snapshot}' set to {score:.1f}")

    elif sub == "get":
        val = get_score(args.store_dir, args.snapshot)
        if val is None:
            print(f"No score set for '{args.snapshot}'")
        else:
            print(f"{args.snapshot}: {val:.1f}")

    elif sub == "remove":
        removed = remove_score(args.store_dir, args.snapshot)
        if removed:
            print(f"Score removed for '{args.snapshot}'")
        else:
            print(f"No score found for '{args.snapshot}'")

    elif sub == "rank":
        asc = getattr(args, "asc", False)
        ranked = rank_snapshots(args.store_dir, descending=not asc)
        if not ranked:
            print("No scored snapshots found.")
        else:
            for name, score in ranked:
                print(f"{score:6.1f}  {name}")


def build_score_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser("score", help="Manage snapshot scores")
    sp = p.add_subparsers(dest="score_cmd", required=True)

    s_set = sp.add_parser("set", help="Assign a score to a snapshot")
    s_set.add_argument("snapshot", help="Snapshot name")
    s_set.add_argument("score", type=float, help="Score between 0.0 and 100.0")

    s_get = sp.add_parser("get", help="Get the score of a snapshot")
    s_get.add_argument("snapshot", help="Snapshot name")

    s_rm = sp.add_parser("remove", help="Remove the score from a snapshot")
    s_rm.add_argument("snapshot", help="Snapshot name")

    s_rank = sp.add_parser("rank", help="List snapshots ranked by score")
    s_rank.add_argument("--asc", action="store_true", help="Sort ascending")

    p.set_defaults(func=cmd_score)
    return p
