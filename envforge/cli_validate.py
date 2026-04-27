"""CLI commands for snapshot validation."""

import argparse
import sys

from envforge.core import load_snapshot
from envforge.validate import format_validation_report, validate_snapshot


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate a snapshot against optional rules passed via CLI flags."""
    try:
        snapshot = load_snapshot(args.snapshot_dir, args.name)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    required = args.require or []
    forbidden = args.forbid or []

    patterns: dict[str, str] = {}
    for item in args.pattern or []:
        if "=" not in item:
            print(f"Invalid pattern spec (expected KEY=REGEX): {item}", file=sys.stderr)
            sys.exit(1)
        key, _, pat = item.partition("=")
        patterns[key.strip()] = pat.strip()

    result = validate_snapshot(snapshot, required=required, forbidden=forbidden, patterns=patterns)
    print(format_validation_report(result))

    if not result["valid"]:
        sys.exit(2)


def build_validate_parser(subparsers: argparse.Action) -> None:
    """Attach the validate sub-command to an existing subparsers group."""
    p = subparsers.add_parser("validate", help="Validate a snapshot against rules")
    p.add_argument("name", help="Snapshot name to validate")
    p.add_argument(
        "--snapshot-dir",
        default=".envforge/snapshots",
        help="Directory containing snapshots",
    )
    p.add_argument(
        "--require",
        metavar="KEY",
        action="append",
        help="Assert that KEY is present (repeatable)",
    )
    p.add_argument(
        "--forbid",
        metavar="KEY",
        action="append",
        help="Assert that KEY is absent (repeatable)",
    )
    p.add_argument(
        "--pattern",
        metavar="KEY=REGEX",
        action="append",
        help="Assert that KEY matches REGEX (repeatable)",
    )
    p.set_defaults(func=cmd_validate)
