"""JSON Schema validation for the DreamPipe job contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "v1" / "dreampipe-job.schema.json"


def validate_job(job: dict[str, Any]) -> None:
    """Raise ValueError with all contract violations, if any."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(job), key=lambda item: list(item.absolute_path))
    if not errors:
        return
    messages = []
    for item in errors:
        path = ".".join(str(part) for part in item.absolute_path) or "<root>"
        messages.append(f"{path}: {item.message}")
    raise ValueError("DreamPipe job violates v1 contract:\n- " + "\n- ".join(messages))
