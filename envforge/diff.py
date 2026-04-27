"""Diff utilities for comparing environment variable snapshots."""

from typing import Any


def diff_snapshots(snapshot_a: dict[str, Any], snapshot_b: dict[str, Any]) -> dict[str, Any]:
    """
    Compare two snapshots and return a structured diff.

    Args:
        snapshot_a: The 'before' snapshot dict (as returned by load_snapshot).
        snapshot_b: The 'after' snapshot dict (as returned by load_snapshot).

    Returns:
        A dict with keys:
            - added:    vars present in b but not in a
            - removed:  vars present in a but not in b
            - changed:  vars present in both but with different values
            - unchanged: vars with identical values in both
    """
    env_a: dict[str, str] = snapshot_a.get("env", {})
    env_b: dict[str, str] = snapshot_b.get("env", {})

    keys_a = set(env_a.keys())
    keys_b = set(env_b.keys())

    added = {k: env_b[k] for k in keys_b - keys_a}
    removed = {k: env_a[k] for k in keys_a - keys_b}
    changed = {
        k: {"before": env_a[k], "after": env_b[k]}
        for k in keys_a & keys_b
        if env_a[k] != env_b[k]
    }
    unchanged = {
        k: env_a[k]
        for k in keys_a & keys_b
        if env_a[k] == env_b[k]
    }

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def format_diff(diff: dict[str, Any], show_unchanged: bool = False) -> str:
    """
    Render a diff dict as a human-readable string.

    Args:
        diff: Output from diff_snapshots().
        show_unchanged: Whether to include unchanged variables in output.

    Returns:
        A formatted multi-line string.
    """
    lines: list[str] = []

    if diff["added"]:
        lines.append("[+] Added:")
        for k, v in sorted(diff["added"].items()):
            lines.append(f"    + {k}={v}")

    if diff["removed"]:
        lines.append("[-] Removed:")
        for k, v in sorted(diff["removed"].items()):
            lines.append(f"    - {k}={v}")

    if diff["changed"]:
        lines.append("[~] Changed:")
        for k, meta in sorted(diff["changed"].items()):
            lines.append(f"    ~ {k}")
            lines.append(f"        before: {meta['before']}")
            lines.append(f"        after:  {meta['after']}")

    if show_unchanged and diff["unchanged"]:
        lines.append("[=] Unchanged:")
        for k, v in sorted(diff["unchanged"].items()):
            lines.append(f"    = {k}={v}")

    if not lines:
        lines.append("No differences found.")

    return "\n".join(lines)
