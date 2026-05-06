"""CLI commands for managing snapshot webhooks."""

from __future__ import annotations

import argparse
from envforge.snapshot_webhook import register_webhook, remove_webhook, list_webhooks

_DEFAULT_DIR = ".envforge"


def cmd_webhook(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "base_dir", _DEFAULT_DIR)

    if args.webhook_cmd == "add":
        events = args.events.split(",") if args.events else None
        entry = register_webhook(base_dir, args.name, args.url, events)
        print(f"Webhook '{args.name}' registered for events: {entry['events']}")

    elif args.webhook_cmd == "remove":
        removed = remove_webhook(base_dir, args.name)
        if removed:
            print(f"Webhook '{args.name}' removed.")
        else:
            print(f"Webhook '{args.name}' not found.")

    elif args.webhook_cmd == "list":
        hooks = list_webhooks(base_dir)
        if not hooks:
            print("No webhooks registered.")
            return
        for name, cfg in hooks.items():
            events_str = ", ".join(cfg.get("events", []))
            print(f"  {name}: {cfg['url']}  [{events_str}]")
    else:
        print("Unknown webhook subcommand.")


def build_webhook_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser("webhook", help="Manage snapshot event webhooks")
    sub = p.add_subparsers(dest="webhook_cmd")

    add_p = sub.add_parser("add", help="Register a webhook")
    add_p.add_argument("name", help="Webhook name")
    add_p.add_argument("url", help="Webhook URL (http/https)")
    add_p.add_argument("--events", help="Comma-separated event list (default: capture,restore,merge)")

    rm_p = sub.add_parser("remove", help="Remove a webhook")
    rm_p.add_argument("name", help="Webhook name")

    sub.add_parser("list", help="List registered webhooks")

    p.set_defaults(func=cmd_webhook)
    return p
