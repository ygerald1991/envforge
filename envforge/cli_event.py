"""CLI commands for managing snapshot event hooks."""

from __future__ import annotations

import argparse

from envforge.snapshot_event import (
    _VALID_EVENTS,
    get_hooks,
    register_hook,
    remove_hook,
)


def cmd_event(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "hooks_dir", ".envforge/hooks")

    if args.event_action == "add":
        entry = register_hook(base_dir, args.event, args.label)
        print(f"Hook '{entry['label']}' registered for event '{entry['event']}'.")

    elif args.event_action == "remove":
        removed = remove_hook(base_dir, args.event, args.label)
        if removed:
            print(f"Hook '{args.label}' removed from event '{args.event}'.")
        else:
            print(f"Hook '{args.label}' not found for event '{args.event}'.")

    elif args.event_action == "list":
        event_filter = getattr(args, "event", None)
        hooks = get_hooks(base_dir, event=event_filter)
        any_found = False
        for event, labels in hooks.items():
            if labels:
                any_found = True
                print(f"{event}:")
                for label in labels:
                    print(f"  - {label}")
        if not any_found:
            print("No hooks registered.")

    else:
        print(f"Unknown action: {args.event_action}")


def build_event_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser("event", help="Manage snapshot lifecycle event hooks")
    sub = p.add_subparsers(dest="event_action", required=True)

    add_p = sub.add_parser("add", help="Register a hook label for an event")
    add_p.add_argument("event", choices=sorted(_VALID_EVENTS))
    add_p.add_argument("label", help="Identifier for this hook")

    rm_p = sub.add_parser("remove", help="Remove a hook label from an event")
    rm_p.add_argument("event", choices=sorted(_VALID_EVENTS))
    rm_p.add_argument("label", help="Identifier of the hook to remove")

    list_p = sub.add_parser("list", help="List registered hooks")
    list_p.add_argument("--event", choices=sorted(_VALID_EVENTS), default=None)

    return p
