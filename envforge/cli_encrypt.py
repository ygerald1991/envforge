"""CLI commands for encrypting and decrypting snapshots."""

import argparse
from pathlib import Path

from envforge.core import load_snapshot, _ensure_snapshot_dir
from envforge.encrypt import (
    generate_key,
    save_encrypted_snapshot,
    load_encrypted_snapshot,
)


def cmd_encrypt(args: argparse.Namespace) -> None:
    """Encrypt an existing snapshot and save it as a .enc file."""
    snap_dir = _ensure_snapshot_dir(args.snapshot_dir)
    source_path = snap_dir / f"{args.name}.json"
    snapshot = load_snapshot(source_path)

    key = args.key or generate_key()
    dest_path = snap_dir / f"{args.name}.enc"
    save_encrypted_snapshot(snapshot, dest_path, key)

    print(f"Encrypted snapshot saved: {dest_path}")
    if not args.key:
        print(f"Generated key (store this safely): {key}")


def cmd_decrypt(args: argparse.Namespace) -> None:
    """Decrypt a .enc snapshot and print or save it as JSON."""
    snap_dir = _ensure_snapshot_dir(args.snapshot_dir)
    enc_path = snap_dir / f"{args.name}.enc"
    snapshot = load_encrypted_snapshot(enc_path, args.key)

    if args.output:
        out_path = Path(args.output)
        import json
        out_path.write_text(json.dumps(snapshot, indent=2))
        print(f"Decrypted snapshot written to: {out_path}")
    else:
        import json
        print(json.dumps(snapshot, indent=2))


def cmd_keygen(args: argparse.Namespace) -> None:
    """Generate and print a new Fernet encryption key."""
    key = generate_key()
    print(key)


def build_encrypt_parser(subparsers) -> None:
    p_enc = subparsers.add_parser("encrypt", help="Encrypt a snapshot")
    p_enc.add_argument("name", help="Snapshot name (without extension)")
    p_enc.add_argument("--key", default=None, help="Fernet key (auto-generated if omitted)")
    p_enc.add_argument("--snapshot-dir", default=None)
    p_enc.set_defaults(func=cmd_encrypt)

    p_dec = subparsers.add_parser("decrypt", help="Decrypt a snapshot")
    p_dec.add_argument("name", help="Snapshot name (without .enc extension)")
    p_dec.add_argument("--key", required=True, help="Fernet key used during encryption")
    p_dec.add_argument("--output", default=None, help="Write decrypted JSON to this file")
    p_dec.add_argument("--snapshot-dir", default=None)
    p_dec.set_defaults(func=cmd_decrypt)

    p_kg = subparsers.add_parser("keygen", help="Generate a new encryption key")
    p_kg.set_defaults(func=cmd_keygen)
