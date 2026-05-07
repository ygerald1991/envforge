"""CLI commands for snapshot signing and verification."""

import argparse
import sys

from envforge.snapshot_signature import (
    get_signature,
    remove_signature,
    sign_snapshot,
    verify_snapshot,
)
from envforge.core import load_snapshot


def cmd_signature(args: argparse.Namespace) -> None:
    if args.sig_cmd == "sign":
        try:
            snapshot = load_snapshot(args.name, args.snapshot_dir)
        except FileNotFoundError:
            print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
            sys.exit(1)
        sig = sign_snapshot(snapshot, args.name, args.secret, args.snapshot_dir)
        print(f"Signed '{args.name}': {sig}")

    elif args.sig_cmd == "verify":
        try:
            snapshot = load_snapshot(args.name, args.snapshot_dir)
        except FileNotFoundError:
            print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
            sys.exit(1)
        try:
            valid = verify_snapshot(snapshot, args.name, args.secret, args.snapshot_dir)
        except KeyError:
            print(f"No signature stored for '{args.name}'.", file=sys.stderr)
            sys.exit(2)
        if valid:
            print(f"Signature valid for '{args.name}'.")
        else:
            print(f"Signature INVALID for '{args.name}'.", file=sys.stderr)
            sys.exit(3)

    elif args.sig_cmd == "show":
        sig = get_signature(args.name, args.snapshot_dir)
        if sig is None:
            print(f"No signature stored for '{args.name}'.")
        else:
            print(f"{args.name}: {sig}")

    elif args.sig_cmd == "remove":
        removed = remove_signature(args.name, args.snapshot_dir)
        if removed:
            print(f"Removed signature for '{args.name}'.")
        else:
            print(f"No signature found for '{args.name}'.")


def build_signature_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is None:
        parser = argparse.ArgumentParser(description="Snapshot signature commands")
        sub = parser.add_subparsers(dest="sig_cmd")
    else:
        parser = subparsers.add_parser("signature", help="Sign and verify snapshots")
        sub = parser.add_subparsers(dest="sig_cmd")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("name", help="Snapshot name")
    common.add_argument("--snapshot-dir", default=".envforge", dest="snapshot_dir")

    p_sign = sub.add_parser("sign", parents=[common], help="Sign a snapshot")
    p_sign.add_argument("--secret", required=True, help="HMAC secret key")

    p_verify = sub.add_parser("verify", parents=[common], help="Verify a snapshot signature")
    p_verify.add_argument("--secret", required=True, help="HMAC secret key")

    sub.add_parser("show", parents=[common], help="Show stored signature")
    sub.add_parser("remove", parents=[common], help="Remove stored signature")

    parser.set_defaults(func=cmd_signature)
    return parser
