"""Snapshot validation: check for required keys, forbidden keys, and value patterns."""

import re
from typing import Any


def validate_required_keys(snapshot: dict[str, Any], required: list[str]) -> list[str]:
    """Return list of required keys missing from snapshot."""
    env = snapshot.get("vars", {})
    return [k for k in required if k not in env]


def validate_forbidden_keys(snapshot: dict[str, Any], forbidden: list[str]) -> list[str]:
    """Return list of forbidden keys that are present in snapshot."""
    env = snapshot.get("vars", {})
    return [k for k in forbidden if k in env]


def validate_value_pattern(
    snapshot: dict[str, Any], key: str, pattern: str
) -> bool:
    """Return True if the value for key matches the given regex pattern."""
    env = snapshot.get("vars", {})
    if key not in env:
        return False
    return bool(re.fullmatch(pattern, env[key]))


def validate_snapshot(
    snapshot: dict[str, Any],
    required: list[str] | None = None,
    forbidden: list[str] | None = None,
    patterns: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run all validations and return a structured result dict.

    Returns:
        {
            "valid": bool,
            "missing_required": [...],
            "present_forbidden": [...],
            "pattern_failures": {key: pattern, ...},
        }
    """
    missing = validate_required_keys(snapshot, required or [])
    present_forbidden = validate_forbidden_keys(snapshot, forbidden or [])

    pattern_failures: dict[str, str] = {}
    for key, pat in (patterns or {}).items():
        if not validate_value_pattern(snapshot, key, pat):
            pattern_failures[key] = pat

    valid = not missing and not present_forbidden and not pattern_failures
    return {
        "valid": valid,
        "missing_required": missing,
        "present_forbidden": present_forbidden,
        "pattern_failures": pattern_failures,
    }


def format_validation_report(result: dict[str, Any]) -> str:
    """Format a validation result dict into a human-readable string."""
    lines = []
    if result["valid"]:
        lines.append("Validation passed.")
        return "\n".join(lines)

    lines.append("Validation FAILED:")
    if result["missing_required"]:
        lines.append("  Missing required keys: " + ", ".join(result["missing_required"]))
    if result["present_forbidden"]:
        lines.append("  Forbidden keys present: " + ", ".join(result["present_forbidden"]))
    if result["pattern_failures"]:
        for key, pat in result["pattern_failures"].items():
            lines.append(f"  Key '{key}' does not match pattern: {pat}")
    return "\n".join(lines)
