"""Template support: create snapshot templates with placeholder values."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

PLACEHOLDER_RE = re.compile(r"^<(.+)>$")


def _get_template_dir(base_dir: str) -> Path:
    path = Path(base_dir) / "templates"
    path.mkdir(parents=True, exist_ok=True)
    return path


def create_template(variables: Dict[str, str], name: str, base_dir: str) -> Path:
    """Save a template JSON file under base_dir/templates/.

    Values that look like '<PLACEHOLDER>' are kept as-is to signal
    required substitution later.
    """
    template_dir = _get_template_dir(base_dir)
    dest = template_dir / f"{name}.json"
    dest.write_text(json.dumps(variables, indent=2))
    return dest


def load_template(name: str, base_dir: str) -> Dict[str, str]:
    """Load a template by name, returning its variable dict."""
    path = _get_template_dir(base_dir) / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Template '{name}' not found in {base_dir}")
    return json.loads(path.read_text())


def list_templates(base_dir: str) -> List[str]:
    """Return sorted template names (without .json extension)."""
    template_dir = _get_template_dir(base_dir)
    return sorted(p.stem for p in template_dir.glob("*.json"))


def get_placeholders(template: Dict[str, str]) -> List[str]:
    """Return keys whose values are placeholder strings like '<VALUE>'."""
    return [k for k, v in template.items() if PLACEHOLDER_RE.match(v)]


def apply_template(
    template: Dict[str, str],
    substitutions: Dict[str, str],
    allow_partial: bool = False,
) -> Dict[str, str]:
    """Fill in placeholder values with substitutions.

    Raises ValueError if any placeholder is unresolved and allow_partial is False.
    """
    result = dict(template)
    for key, value in result.items():
        m = PLACEHOLDER_RE.match(value)
        if m:
            placeholder_name = m.group(1)
            if placeholder_name in substitutions:
                result[key] = substitutions[placeholder_name]
            elif key in substitutions:
                result[key] = substitutions[key]
    unresolved = get_placeholders(result)
    if unresolved and not allow_partial:
        raise ValueError(f"Unresolved placeholders for keys: {unresolved}")
    return result
