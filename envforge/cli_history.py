"""CLI commands for snapshot history management."""

from __future__ import annotations

import argparse
import sys

from envforge.history import get_snapshot_history, prune_history, format_history


def cmd_history(args: argparse.Namespace) -> None:
    """Display snapshot history, optionally filtered by prefix."""
    history = get_snapshot_history(args.snapshot_dir, prefix=getattr(args, "prefix", None))
    print(format_history(history))


def cmd_prune(args: argparse.Namespace) -> None:
    """Prune old snapshots, keeping the N most recent."""
    dry_run = getattr(args, "dry_run", False)
    deleted = prune_history(
        args.snapshot_dir,
        keep=args.keep,
        prefix=getattr(args, "prefix", None),
        dry_run=dry_run,
    )

    if not deleted:
        print("Nothing to prune.")
        return

    verb = "Would delete" if dry_run else "Deleted"
    for name in deleted:
        print(f"{verb}: {name}")
    print(f"\n{verb} {len(deleted)} snapshot(s).")


def build_history_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'history' and 'prune' sub-commands."""
    # history
    p_hist = subparsers.add_parser("history", help="Show snapshot history")
    p_hist.add_argument("--snapshot-dir", default=".snapshots", help="Snapshot directory")
    p_hist.add_argument("--prefix", default=None, help="Filter snapshots by name prefix")
    p_hist.set_defaults(func=cmd_history)

    # prune
    p_prune = subparsers.add_parser("prune", help="Remove old snapshots")
    p_prune.add_argument("--snapshot-dir", default=".snapshots", help="Snapshot directory")
    p_prune.add_argument("--keep", type=int, required=True, help="Number of snapshots to keep")
    p_prune.add_argument("--prefix", default=None, help="Limit pruning to snapshots with this prefix")
    p_prune.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    p_prune.set_defaults(func=cmd_prune)
