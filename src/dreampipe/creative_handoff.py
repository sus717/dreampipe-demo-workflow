"""Load and validate Pod 2's model-agnostic creative handoff files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


class CreativeHandoffError(ValueError):
    """Raised when a creative handoff cannot safely enter the pipeline."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CreativeHandoffError(f"Creative handoff file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CreativeHandoffError(f"Creative handoff file is invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise CreativeHandoffError(f"Creative handoff file must contain a JSON object: {path}")
    return value


def _validate(value: Mapping[str, Any], schema_name: str) -> None:
    schema_path = ROOT / "shared" / "schemas" / schema_name
    schema = _read_json(schema_path)
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        messages = "; ".join(
            f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise CreativeHandoffError(f"{schema_name} validation failed: {messages}")


def load_creative_handoff(
    job: Mapping[str, Any],
    *,
    project_bible_path: str | Path | None = None,
    shots_path: str | Path | None = None,
) -> dict[str, Any]:
    """Return Pod 2's frozen Bible and shot list after cross-contract checks."""
    project_bible = _read_json(Path(project_bible_path or ROOT / "shared" / "project_bible.json"))
    shots_document = _read_json(Path(shots_path or ROOT / "shared" / "shots.json"))
    _validate(project_bible, "project_bible.schema.json")
    _validate(shots_document, "shots.schema.json")

    project_id = str(job["job_id"])
    if project_bible.get("project_id") != project_id or shots_document.get("project_id") != project_id:
        raise CreativeHandoffError("Creative handoff project_id must match the LangGraph job_id.")
    brief = job["creative_brief"]
    if shots_document.get("aspect_ratio") != brief["aspect_ratio"]:
        raise CreativeHandoffError("Shot list aspect_ratio must match the approved Brief.")
    if shots_document.get("target_duration_seconds") != brief["duration_seconds"]:
        raise CreativeHandoffError("Shot list target_duration_seconds must match the approved Brief.")
    expected_count = int(job.get("expected_shot_count", 3))
    if len(shots_document["shots"]) != expected_count:
        raise CreativeHandoffError(f"Shot list must contain exactly {expected_count} shots for this MVP.")

    return {"project_bible": project_bible, "shots": shots_document["shots"]}
