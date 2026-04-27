"""CLI command for the envforge audit log."""

import argparse
import sys
from pathlib import Path

from envforge.audit import read_audit_log, format_audit_log
from envforge.core import _ensure_snapshot_dir


def cmd_audit(args: argparse.Namespace) -> int:
    """Display the audit log for the snapshot directory."""
    snapshot_dir = _ensure_snapshot_dir(args.snapshot_dir)
    entries = read_audit_log(snapshot_dir)

    if getattr(args, "tail", None):
        entries = entries[-args.tail :]

    if getattr(args, "action", None):
        entries = [e for e in entries if e["action"] == args.action]

    print(format_audit_log(entries))
    return 0


def build_audit_parser(subparsers) -> None:
    """Register the 'audit' subcommand on an existing subparsers object."""
    parser = subparsers.add_parser(
        "audit",
        help="Show the audit log of snapshot operations.",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=None,
        help="Path to snapshot directory (default: ~/.envforge/snapshots).",
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=None,
        metavar="N",
        help="Show only the last N entries.",
    )
    parser.add_argument(
        "--action",
        default=None,
        help="Filter entries by action name (e.g. capture, restore).",
    )
    parser.set_defaults(func=cmd_audit)
