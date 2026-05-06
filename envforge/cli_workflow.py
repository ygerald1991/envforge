"""CLI commands for snapshot workflows."""

from __future__ import annotations

import argparse
from envforge.snapshot_workflow import (
    create_workflow,
    get_workflow,
    list_workflows,
    delete_workflow,
    append_step,
)


def cmd_workflow(args: argparse.Namespace) -> None:
    base = args.base_dir

    if args.workflow_action == "create":
        result = create_workflow(base, args.name, args.steps)
        print(f"Workflow '{result['name']}' created with {len(result['steps'])} step(s).")

    elif args.workflow_action == "show":
        steps = get_workflow(base, args.name)
        if steps is None:
            print(f"Workflow '{args.name}' not found.")
        else:
            print(f"Workflow '{args.name}':")
            for i, step in enumerate(steps, 1):
                print(f"  {i}. {step}")

    elif args.workflow_action == "list":
        names = list_workflows(base)
        if not names:
            print("No workflows defined.")
        else:
            for name in names:
                print(name)

    elif args.workflow_action == "delete":
        removed = delete_workflow(base, args.name)
        if removed:
            print(f"Workflow '{args.name}' deleted.")
        else:
            print(f"Workflow '{args.name}' not found.")

    elif args.workflow_action == "append":
        steps = append_step(base, args.name, args.snapshot)
        print(f"Appended '{args.snapshot}' to workflow '{args.name}' ({len(steps)} step(s) total).")


def build_workflow_parser(subparsers: argparse.Action) -> None:
    p = subparsers.add_parser("workflow", help="Manage snapshot promotion workflows")
    p.add_argument("--base-dir", default=".envforge", dest="base_dir")
    sub = p.add_subparsers(dest="workflow_action", required=True)

    c = sub.add_parser("create", help="Create a workflow")
    c.add_argument("name")
    c.add_argument("steps", nargs="+")

    s = sub.add_parser("show", help="Show workflow steps")
    s.add_argument("name")

    sub.add_parser("list", help="List all workflows")

    d = sub.add_parser("delete", help="Delete a workflow")
    d.add_argument("name")

    a = sub.add_parser("append", help="Append a step to a workflow")
    a.add_argument("name")
    a.add_argument("snapshot")

    p.set_defaults(func=cmd_workflow)
