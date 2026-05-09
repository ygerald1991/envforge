"""CLI commands for snapshot permission management."""

from __future__ import annotations

import argparse
from typing import Optional

from envforge.snapshot_permission import (
    set_permission,
    remove_permission,
    get_permission,
    list_permissions,
    VALID_ROLES,
)


def cmd_permission(args: argparse.Namespace, base_dir: Optional[str] = None) -> None:
    bdir = base_dir or args.base_dir

    if args.perm_cmd == "grant":
        result = set_permission(bdir, args.snapshot, args.user, args.role)
        print(f"Granted '{result['role']}' to '{result['user']}' on '{result['snapshot']}'.")

    elif args.perm_cmd == "revoke":
        removed = remove_permission(bdir, args.snapshot, args.user)
        if removed:
            print(f"Revoked access for '{args.user}' on '{args.snapshot}'.")
        else:
            print(f"No permission found for '{args.user}' on '{args.snapshot}'.")

    elif args.perm_cmd == "get":
        role = get_permission(bdir, args.snapshot, args.user)
        if role:
            print(f"'{args.user}' has role '{role}' on '{args.snapshot}'.")
        else:
            print(f"No permission found for '{args.user}' on '{args.snapshot}'.")

    elif args.perm_cmd == "list":
        perms = list_permissions(bdir, args.snapshot)
        if not perms:
            print(f"No permissions set for '{args.snapshot}'.")
        else:
            for user, role in sorted(perms.items()):
                print(f"  {user}: {role}")


def build_permission_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("permission", help="Manage snapshot permissions")
    p.add_argument("--base-dir", default=".envforge", dest="base_dir")
    sub = p.add_subparsers(dest="perm_cmd", required=True)

    grant = sub.add_parser("grant", help="Grant a role to a user")
    grant.add_argument("snapshot")
    grant.add_argument("user")
    grant.add_argument("role", choices=sorted(VALID_ROLES))

    revoke = sub.add_parser("revoke", help="Revoke a user's access")
    revoke.add_argument("snapshot")
    revoke.add_argument("user")

    get_p = sub.add_parser("get", help="Get a user's role on a snapshot")
    get_p.add_argument("snapshot")
    get_p.add_argument("user")

    lst = sub.add_parser("list", help="List all permissions for a snapshot")
    lst.add_argument("snapshot")

    p.set_defaults(func=cmd_permission)
