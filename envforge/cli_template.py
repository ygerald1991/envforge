"""CLI commands for snapshot template management."""

from __future__ import annotations

import argparse
import json
import os
from typing import List, Optional

from envforge.template import (
    apply_template,
    create_template,
    get_placeholders,
    list_templates,
    load_template,
)


def cmd_template(args: argparse.Namespace) -> None:
    sub = args.template_cmd

    if sub == "create":
        raw: dict = json.loads(args.vars_json)
        dest = create_template(raw, args.name, args.dir)
        print(f"Template '{args.name}' saved to {dest}")

    elif sub == "list":
        names = list_templates(args.dir)
        if not names:
            print("No templates found.")
        else:
            for n in names:
                print(n)

    elif sub == "show":
        tmpl = load_template(args.name, args.dir)
        placeholders = get_placeholders(tmpl)
        print(json.dumps(tmpl, indent=2))
        if placeholders:
            print(f"\nPlaceholders: {', '.join(placeholders)}")

    elif sub == "apply":
        tmpl = load_template(args.name, args.dir)
        subs: dict = json.loads(args.subs_json) if args.subs_json else {}
        result = apply_template(tmpl, subs, allow_partial=args.partial)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown template subcommand: {sub}")


def build_template_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("template", help="Manage snapshot templates")
    p.add_argument("--dir", default=".envforge", help="Snapshot base directory")
    sub = p.add_subparsers(dest="template_cmd")

    c = sub.add_parser("create", help="Create a new template")
    c.add_argument("name", help="Template name")
    c.add_argument("vars_json", help="JSON object of variable key/value pairs")

    sub.add_parser("list", help="List available templates")

    s = sub.add_parser("show", help="Show a template and its placeholders")
    s.add_argument("name", help="Template name")

    a = sub.add_parser("apply", help="Apply substitutions to a template")
    a.add_argument("name", help="Template name")
    a.add_argument("--subs", dest="subs_json", default="{}", help="JSON substitutions")
    a.add_argument("--partial", action="store_true", help="Allow unresolved placeholders")

    p.set_defaults(func=cmd_template)
