"""CLI commands for snapshot comparison."""

import argparse
from envforge.compare import compare_snapshots, format_comparison


def cmd_compare(args: argparse.Namespace) -> None:
    """Handle the 'compare' CLI subcommand."""
    try:
        comparison = compare_snapshots(args.snapshots, base_dir=getattr(args, "base_dir", None))
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return

    show_all = getattr(args, "all", False)
    output = format_comparison(comparison, show_all=show_all)
    print(output, end="")

    drift = comparison["drift"]
    if drift:
        print(f"Drifted keys ({len(drift)}): {', '.join(drift)}")
    else:
        print("All snapshots are in sync.")


def build_compare_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Register the 'compare' subcommand."""
    parser = subparsers.add_parser(
        "compare",
        help="Compare two or more snapshots side-by-side and highlight drift.",
    )
    parser.add_argument(
        "snapshots",
        nargs="+",
        metavar="SNAPSHOT",
        help="Two or more snapshot names to compare.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Show all keys, not just those with drift.",
    )
    parser.add_argument(
        "--base-dir",
        default=None,
        metavar="DIR",
        help="Override the snapshot storage directory.",
    )
    parser.set_defaults(func=cmd_compare)
    return parser
