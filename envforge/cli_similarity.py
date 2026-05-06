"""CLI commands for snapshot similarity scoring."""

from __future__ import annotations

import argparse
import os

from envforge.core import list_snapshots
from envforge.snapshot_similarity import compare_similarity, rank_by_similarity

_DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".envforge", "snapshots")


def cmd_similarity(args: argparse.Namespace) -> None:
    snapshot_dir = getattr(args, "snapshot_dir", _DEFAULT_DIR)

    if args.sub == "compare":
        scores = compare_similarity(snapshot_dir, args.snapshot_a, args.snapshot_b)
        print(f"Key similarity  : {scores['key_similarity']:.4f}")
        print(f"Value similarity: {scores['value_similarity']:.4f}")

    elif args.sub == "rank":
        candidates = args.against or [
            n for n in list_snapshots(snapshot_dir) if n != args.reference
        ]
        if not candidates:
            print("No candidate snapshots found.")
            return
        ranked = rank_by_similarity(
            snapshot_dir, args.reference, candidates, mode=args.mode
        )
        print(f"Ranked by {args.mode} similarity against '{args.reference}':")
        for rank, (name, score) in enumerate(ranked, 1):
            print(f"  {rank:>3}. {name:<40} {score:.4f}")


def build_similarity_parser(
    parent: "argparse._SubParsersAction | None" = None,
) -> argparse.ArgumentParser:
    kwargs = dict(description="Compute similarity between snapshots.")
    if parent is not None:
        parser = parent.add_parser("similarity", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    sub = parser.add_subparsers(dest="sub", required=True)

    # compare sub-command
    cmp = sub.add_parser("compare", help="Compare two snapshots directly.")
    cmp.add_argument("snapshot_a", help="First snapshot name.")
    cmp.add_argument("snapshot_b", help="Second snapshot name.")

    # rank sub-command
    rank = sub.add_parser("rank", help="Rank all snapshots by similarity to a reference.")
    rank.add_argument("reference", help="Reference snapshot name.")
    rank.add_argument(
        "--against",
        nargs="+",
        metavar="SNAPSHOT",
        default=None,
        help="Specific snapshots to rank (default: all others).",
    )
    rank.add_argument(
        "--mode",
        choices=["key", "value"],
        default="value",
        help="Similarity metric to use (default: value).",
    )

    parser.set_defaults(func=cmd_similarity)
    return parser
