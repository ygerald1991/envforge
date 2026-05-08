"""CLI commands for managing snapshot trigger rules."""

import argparse

from envforge.snapshot_trigger import (
    set_trigger,
    get_trigger,
    remove_trigger,
    list_triggers,
    set_trigger_enabled,
    VALID_CONDITIONS,
)

_DEFAULT_STORE = ".envforge"


def cmd_trigger(args: argparse.Namespace) -> None:
    store = getattr(args, "store", _DEFAULT_STORE)

    if args.trigger_action == "set":
        entry = set_trigger(store, args.name, args.condition, args.prefix)
        print(
            f"Trigger '{args.name}' set: condition={entry['condition']}, "
            f"prefix={entry['prefix']}, enabled={entry['enabled']}"
        )

    elif args.trigger_action == "get":
        entry = get_trigger(store, args.name)
        if entry is None:
            print(f"No trigger found for '{args.name}'.")
        else:
            print(
                f"{args.name}: condition={entry['condition']}, "
                f"prefix={entry['prefix']}, enabled={entry['enabled']}"
            )

    elif args.trigger_action == "remove":
        removed = remove_trigger(store, args.name)
        if removed:
            print(f"Trigger '{args.name}' removed.")
        else:
            print(f"Trigger '{args.name}' not found.")

    elif args.trigger_action == "list":
        rules = list_triggers(store)
        if not rules:
            print("No trigger rules registered.")
        else:
            for name, entry in rules.items():
                status = "enabled" if entry["enabled"] else "disabled"
                print(f"  {name}: [{status}] condition={entry['condition']}, prefix={entry['prefix']}")

    elif args.trigger_action == "enable":
        entry = set_trigger_enabled(store, args.name, True)
        print(f"Trigger '{args.name}' enabled.")

    elif args.trigger_action == "disable":
        entry = set_trigger_enabled(store, args.name, False)
        print(f"Trigger '{args.name}' disabled.")


def build_trigger_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser("trigger", help="Manage snapshot trigger rules")
    sub = p.add_subparsers(dest="trigger_action", required=True)

    s = sub.add_parser("set", help="Create or update a trigger rule")
    s.add_argument("name", help="Rule name")
    s.add_argument("condition", choices=sorted(VALID_CONDITIONS), help="Trigger condition")
    s.add_argument("--prefix", default="auto", help="Snapshot name prefix (default: auto)")

    g = sub.add_parser("get", help="Show a trigger rule")
    g.add_argument("name")

    r = sub.add_parser("remove", help="Delete a trigger rule")
    r.add_argument("name")

    sub.add_parser("list", help="List all trigger rules")

    en = sub.add_parser("enable", help="Enable a trigger rule")
    en.add_argument("name")

    dis = sub.add_parser("disable", help="Disable a trigger rule")
    dis.add_argument("name")

    p.set_defaults(func=cmd_trigger)
    return p
