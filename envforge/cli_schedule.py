"""CLI commands for managing automatic snapshot schedules."""

import argparse
from envforge.schedule import (
    set_schedule,
    remove_schedule,
    list_schedules,
    get_due_schedules,
    mark_ran,
)
from envforge.core import capture_env, save_snapshot
from datetime import datetime


def cmd_schedule(args: argparse.Namespace) -> None:
    action = args.schedule_action

    if action == "set":
        entry = set_schedule(
            name=args.name,
            interval_seconds=args.interval,
            label_prefix=args.prefix,
            base_dir=args.dir,
        )
        print(f"Schedule '{args.name}' set: every {args.interval}s (prefix='{args.prefix}')")

    elif action == "remove":
        removed = remove_schedule(name=args.name, base_dir=args.dir)
        if removed:
            print(f"Schedule '{args.name}' removed.")
        else:
            print(f"Schedule '{args.name}' not found.")

    elif action == "list":
        schedules = list_schedules(base_dir=args.dir)
        if not schedules:
            print("No schedules configured.")
        else:
            for name, entry in schedules.items():
                last = entry.get("last_run") or "never"
                print(f"  {name}: every {entry['interval_seconds']}s, last_run={last}")

    elif action == "run-due":
        due = get_due_schedules(base_dir=args.dir)
        if not due:
            print("No schedules are due.")
            return
        for name in due:
            schedules = list_schedules(base_dir=args.dir)
            entry = schedules[name]
            prefix = entry.get("label_prefix", "auto")
            label = f"{prefix}-{name}-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
            env = capture_env()
            save_snapshot(label, env, base_dir=args.dir)
            mark_ran(name, base_dir=args.dir)
            print(f"Snapshot saved for schedule '{name}': {label}")


def build_schedule_parser(subparsers) -> None:
    p = subparsers.add_parser("schedule", help="Manage automatic snapshot schedules")
    p.add_argument("--dir", default=".", help="Base directory for schedule config")
    sub = p.add_subparsers(dest="schedule_action")

    p_set = sub.add_parser("set", help="Create or update a schedule")
    p_set.add_argument("name", help="Schedule name")
    p_set.add_argument("--interval", type=int, default=3600, help="Interval in seconds")
    p_set.add_argument("--prefix", default="auto", help="Snapshot label prefix")

    p_rm = sub.add_parser("remove", help="Remove a schedule")
    p_rm.add_argument("name", help="Schedule name")

    sub.add_parser("list", help="List all schedules")
    sub.add_parser("run-due", help="Run all due schedules and save snapshots")

    p.set_defaults(func=cmd_schedule)
