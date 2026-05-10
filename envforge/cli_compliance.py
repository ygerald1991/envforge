"""CLI commands for snapshot compliance rules."""

from __future__ import annotations

import argparse
import json
import sys

from envforge.snapshot_compliance import (
    check_compliance,
    get_compliance_rule,
    list_compliance_rules,
    remove_compliance_rule,
    set_compliance_rule,
)


def cmd_compliance(args: argparse.Namespace) -> None:
    sub = args.compliance_sub

    if sub == "set":
        rule: dict = {}
        if args.required_prefix:
            rule["required_prefix"] = args.required_prefix
        if args.key_pattern:
            rule["key_pattern"] = args.key_pattern
        if args.max_keys is not None:
            rule["max_keys"] = args.max_keys
        if not rule:
            print("Error: at least one rule field must be specified.", file=sys.stderr)
            sys.exit(1)
        set_compliance_rule(args.base_dir, args.rule_name, rule)
        print(f"Compliance rule '{args.rule_name}' saved.")

    elif sub == "get":
        rule = get_compliance_rule(args.base_dir, args.rule_name)
        if rule is None:
            print(f"No rule found: {args.rule_name}")
        else:
            print(json.dumps(rule, indent=2))

    elif sub == "list":
        rules = list_compliance_rules(args.base_dir)
        if not rules:
            print("No compliance rules defined.")
        else:
            for name, body in rules.items():
                print(f"{name}: {json.dumps(body)}")

    elif sub == "remove":
        removed = remove_compliance_rule(args.base_dir, args.rule_name)
        if removed:
            print(f"Compliance rule '{args.rule_name}' removed.")
        else:
            print(f"Rule not found: {args.rule_name}")

    elif sub == "check":
        try:
            variables = json.loads(args.variables_json)
        except json.JSONDecodeError as exc:
            print(f"Invalid JSON for variables: {exc}", file=sys.stderr)
            sys.exit(1)
        try:
            violations = check_compliance(
                args.base_dir, args.snapshot_name, variables, args.rule_name
            )
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)
        if violations:
            print("Compliance violations found:")
            for v in violations:
                print(f"  - {v}")
            sys.exit(2)
        else:
            print("Compliant.")


def build_compliance_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("compliance", help="Manage compliance rules")
    p.add_argument("--base-dir", default=".envforge", dest="base_dir")
    subs = p.add_subparsers(dest="compliance_sub")

    s = subs.add_parser("set", help="Create or update a rule")
    s.add_argument("rule_name")
    s.add_argument("--required-prefix", default="")
    s.add_argument("--key-pattern", default="")
    s.add_argument("--max-keys", type=int, default=None)

    g = subs.add_parser("get", help="Show a rule")
    g.add_argument("rule_name")

    subs.add_parser("list", help="List all rules")

    r = subs.add_parser("remove", help="Delete a rule")
    r.add_argument("rule_name")

    c = subs.add_parser("check", help="Check a snapshot against a rule")
    c.add_argument("rule_name")
    c.add_argument("snapshot_name")
    c.add_argument("variables_json", help="JSON object of env vars to check")

    p.set_defaults(func=cmd_compliance)
