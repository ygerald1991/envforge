"""CLI commands for snapshot dependency management."""

import argparse
from envforge.snapshot_deps import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    get_all_dependencies,
)


def cmd_deps(args: argparse.Namespace) -> None:
    base_dir = getattr(args, "base_dir", ".")

    if args.deps_action == "add":
        add_dependency(base_dir, args.snapshot, args.depends_on)
        print(f"Dependency added: '{args.snapshot}' depends on '{args.depends_on}'.")

    elif args.deps_action == "remove":
        removed = remove_dependency(base_dir, args.snapshot, args.depends_on)
        if removed:
            print(f"Dependency removed: '{args.snapshot}' no longer depends on '{args.depends_on}'.")
        else:
            print(f"No such dependency: '{args.snapshot}' -> '{args.depends_on}'.")

    elif args.deps_action == "list":
        deps = get_dependencies(base_dir, args.snapshot)
        if not deps:
            print(f"'{args.snapshot}' has no recorded dependencies.")
        else:
            print(f"Dependencies of '{args.snapshot}':")
            for d in deps:
                print(f"  - {d}")

    elif args.deps_action == "dependents":
        dependents = get_dependents(base_dir, args.snapshot)
        if not dependents:
            print(f"No snapshots depend on '{args.snapshot}'.")
        else:
            print(f"Snapshots that depend on '{args.snapshot}':")
            for d in dependents:
                print(f"  - {d}")

    elif args.deps_action == "all":
        all_deps = get_all_dependencies(base_dir)
        if not all_deps:
            print("No dependencies recorded.")
        else:
            for snap, parents in all_deps.items():
                print(f"{snap}: {', '.join(parents)}")


def build_deps_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("deps", help="Manage snapshot dependencies")
    sub = p.add_subparsers(dest="deps_action", required=True)

    add_p = sub.add_parser("add", help="Add a dependency")
    add_p.add_argument("snapshot")
    add_p.add_argument("depends_on")

    rm_p = sub.add_parser("remove", help="Remove a dependency")
    rm_p.add_argument("snapshot")
    rm_p.add_argument("depends_on")

    ls_p = sub.add_parser("list", help="List dependencies of a snapshot")
    ls_p.add_argument("snapshot")

    dep_p = sub.add_parser("dependents", help="List snapshots that depend on a given snapshot")
    dep_p.add_argument("snapshot")

    sub.add_parser("all", help="Show all recorded dependencies")

    p.set_defaults(func=cmd_deps)
