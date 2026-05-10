"""Snapshot compliance checks: enforce naming conventions, required prefixes, and key count limits."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _get_compliance_path(base_dir: str) -> Path:
    return Path(base_dir) / "compliance_rules.json"


def _load_rules(base_dir: str) -> dict:
    p = _get_compliance_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_rules(base_dir: str, rules: dict) -> None:
    p = _get_compliance_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rules, indent=2))


def set_compliance_rule(base_dir: str, rule_name: str, rule: dict) -> dict:
    """Add or update a named compliance rule.

    Supported rule keys:
      - required_prefix (str): snapshot name must start with this
      - key_pattern (str): all env keys must match this regex
      - max_keys (int): snapshot may not exceed this many keys
    """
    allowed = {"required_prefix", "key_pattern", "max_keys"}
    unknown = set(rule) - allowed
    if unknown:
        raise ValueError(f"Unknown rule fields: {unknown}")
    rules = _load_rules(base_dir)
    rules[rule_name] = rule
    _save_rules(base_dir, rules)
    return rules[rule_name]


def get_compliance_rule(base_dir: str, rule_name: str) -> dict | None:
    return _load_rules(base_dir).get(rule_name)


def list_compliance_rules(base_dir: str) -> dict:
    return _load_rules(base_dir)


def remove_compliance_rule(base_dir: str, rule_name: str) -> bool:
    rules = _load_rules(base_dir)
    if rule_name not in rules:
        return False
    del rules[rule_name]
    _save_rules(base_dir, rules)
    return True


def check_compliance(
    base_dir: str,
    snapshot_name: str,
    variables: dict[str, str],
    rule_name: str,
) -> list[str]:
    """Return a list of violation messages (empty list = compliant)."""
    rule = get_compliance_rule(base_dir, rule_name)
    if rule is None:
        raise KeyError(f"Compliance rule not found: {rule_name}")

    violations: list[str] = []

    if "required_prefix" in rule:
        prefix = rule["required_prefix"]
        if not snapshot_name.startswith(prefix):
            violations.append(
                f"Snapshot name '{snapshot_name}' must start with '{prefix}'"
            )

    if "key_pattern" in rule:
        pattern = re.compile(rule["key_pattern"])
        bad_keys = [k for k in variables if not pattern.match(k)]
        if bad_keys:
            violations.append(
                f"Keys do not match pattern '{rule['key_pattern']}': {bad_keys}"
            )

    if "max_keys" in rule:
        if len(variables) > rule["max_keys"]:
            violations.append(
                f"Snapshot has {len(variables)} keys, exceeding max_keys={rule['max_keys']}"
            )

    return violations
