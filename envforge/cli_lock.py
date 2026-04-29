"""CLI commands for locking and unlocking snapshots."""

import argparse
from envforge.lock import lock_snapshot, unlock_snapshot, is_locked, list_locked

_DEFAULT_DIR = ".snapshots"


def cmd_lock(args) -> None:
    snapshot_dir = getattr(args, "snapshot_dir", _DEFAULT_DIR)
    name = args.name
    if is_locked(snapshot_dir, name):
        print(f"Snapshot '{name}' is already locked.")
        return
    lock_snapshot(snapshot_dir, name)
    print(f"Locked snapshot '{name}'.")


def cmd_unlock(args) -> None:
    snapshot_dir = getattr(args, "snapshot_dir", _DEFAULT_DIR)
    name = args.name
    if not is_locked(snapshot_dir, name):
        print(f"Snapshot '{name}' is not locked.")
        return
    unlock_snapshot(snapshot_dir, name)
    print(f"Unlocked snapshot '{name}'.")


def cmd_lock_list(args) -> None:
    snapshot_dir = getattr(args, "snapshot_dir", _DEFAULT_DIR)
    locked = list_locked(snapshot_dir)
    if not locked:
        print("No locked snapshots.")
        return
    print("Locked snapshots:")
    for name in locked:
        print(f"  {name}")


def build_lock_parser(subparsers=None):
    if subparsers is None:
        parser = argparse.ArgumentParser(description="Lock/unlock snapshot commands")
        sub = parser.add_subparsers(dest="lock_cmd")
    else:
        parser = subparsers.add_parser("lock", help="Lock/unlock snapshots")
        sub = parser.add_subparsers(dest="lock_cmd")

    p_lock = sub.add_parser("add", help="Lock a snapshot")
    p_lock.add_argument("name", help="Snapshot name")
    p_lock.set_defaults(func=cmd_lock)

    p_unlock = sub.add_parser("remove", help="Unlock a snapshot")
    p_unlock.add_argument("name", help="Snapshot name")
    p_unlock.set_defaults(func=cmd_unlock)

    p_list = sub.add_parser("list", help="List locked snapshots")
    p_list.set_defaults(func=cmd_lock_list)

    return parser
