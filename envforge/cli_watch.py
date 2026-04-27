"""CLI commands for the env-watch feature."""

import argparse
import sys
from envforge.watch import watch_env, get_watch_snapshots
from envforge.diff import format_diff


def cmd_watch(args: argparse.Namespace) -> None:
    """Start watching the environment for changes."""
    print(
        f"Watching environment every {args.interval}s "
        f"(prefix={args.prefix}, max={args.max_snapshots or 'unlimited'}) ..."
    )
    print("Press Ctrl+C to stop.")

    def _on_change(diff: dict) -> None:
        print("\n[envforge-watch] Change detected:")
        print(format_diff(diff))

    try:
        saved = watch_env(
            interval=args.interval,
            snapshot_dir=args.snapshot_dir,
            prefix=args.prefix,
            max_snapshots=args.max_snapshots,
            on_change=_on_change,
        )
    except KeyboardInterrupt:
        saved = []

    if saved:
        print(f"\nSaved {len(saved)} snapshot(s): {', '.join(saved)}")
    else:
        print("\nNo changes detected.")


def cmd_watch_list(args: argparse.Namespace) -> None:
    """List snapshots created by the watcher."""
    snaps = get_watch_snapshots(
        prefix=args.prefix,
        snapshot_dir=args.snapshot_dir,
    )
    if not snaps:
        print("No watch snapshots found.")
        return
    for s in sorted(snaps):
        print(s)


def build_watch_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("watch", help="Watch for environment changes")
    sub = p.add_subparsers(dest="watch_cmd")

    start = sub.add_parser("start", help="Start watching")
    start.add_argument("--interval", type=float, default=5.0, help="Poll interval in seconds")
    start.add_argument("--prefix", default="watch", help="Snapshot name prefix")
    start.add_argument("--max-snapshots", type=int, default=0, dest="max_snapshots")
    start.add_argument("--snapshot-dir", default=".envforge", dest="snapshot_dir")
    start.set_defaults(func=cmd_watch)

    lst = sub.add_parser("list", help="List watch snapshots")
    lst.add_argument("--prefix", default="watch")
    lst.add_argument("--snapshot-dir", default=".envforge", dest="snapshot_dir")
    lst.set_defaults(func=cmd_watch_list)
