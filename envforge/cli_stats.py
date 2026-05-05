"""CLI sub-commands for snapshot statistics."""

from __future__ import annotations

import argparse
import json
import os

from envforge.snapshot_stats import (
    format_summary,
    key_frequency,
    most_common_keys,
    snapshot_summary,
)

_DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".envforge", "snapshots")


def cmd_stats(args: argparse.Namespace) -> None:
    """Handle the 'stats' command."""
    snap_dir = getattr(args, "snapshot_dir", _DEFAULT_DIR)
    sub = getattr(args, "stats_sub", "summary")

    if sub == "summary":
        summary = snapshot_summary(snap_dir)
        if getattr(args, "json", False):
            print(json.dumps(summary, default=list, indent=2))
        else:
            print(format_summary(summary))

    elif sub == "freq":
        freq = key_frequency(snap_dir)
        top_n = getattr(args, "top", None)
        items = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
        if top_n:
            items = items[:top_n]
        if getattr(args, "json", False):
            print(json.dumps(dict(items), indent=2))
        else:
            for key, count in items:
                print(f"{key:<40} {count}")

    else:
        print(f"Unknown stats sub-command: {sub}")


def build_stats_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'stats' and its sub-commands onto *subparsers*."""
    parser = subparsers.add_parser("stats", help="Show statistics across snapshots")
    parser.add_argument(
        "--snapshot-dir",
        dest="snapshot_dir",
        default=_DEFAULT_DIR,
        help="Directory containing snapshots",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output as JSON",
    )

    sub = parser.add_subparsers(dest="stats_sub")
    sub.add_parser("summary", help="High-level summary (default)")

    freq_p = sub.add_parser("freq", help="Key frequency across snapshots")
    freq_p.add_argument("--top", type=int, default=None, help="Limit to top N keys")

    parser.set_defaults(func=cmd_stats, stats_sub="summary")
