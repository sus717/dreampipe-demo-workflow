"""Normalize Pod 1's Brief v2 into the DreamPipe job contract."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    safe = "".join(char.lower() if char.isalnum() else "_" for char in value)
    return safe.strip("_") or "asset"


def _platform(value: str) -> str:
    values = {
        "douyin": "douyin",
        "抖音": "douyin",
        "tiktok": "tiktok",
        "instagram": "instagram",
        "youtube": "youtube",
    }
    return values.get(value.strip().lower(), "other")


def _flatten_must_show(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if not isinstance(value, dict):
        return [str(value)] if value else []
    output: list[str] = []
    for key, item in value.items():
        if isinstance(item, list):
            output.extend(str(entry) for entry in item)
        elif item:
            output.append(f"{key}: {item}")
    return output


def normalize_brief_v2(source: dict[str, Any], *, source_path: str | None = None) -> dict[str, Any]:
    """Return a contract-shaped initial job without mutating the source Brief.

    The source format is intentionally kept separate: supplied `reference_images`
    become stable asset IDs and `budget.amount/currency` becomes `budget_cny`.
    Location, brand tone and source constraints are preserved in fields consumed
    by the downstream agents rather than discarded.
    """
    required = ["project_id", "product", "audience", "platform", "duration_seconds", "aspect_ratio", "cta"]
    missing = [field for field in required if field not in source]
    if missing:
        raise ValueError(f"Brief v2 missing required fields: {', '.join(missing)}")
    product_source = source["product"]
    reference_images = product_source.get("reference_images") or []

    assets: list[dict[str, Any]] = []
    reference_asset_ids: list[str] = [str(item) for item in product_source.get("reference_asset_ids", [])]
    for index, reference in enumerate(reference_images, start=1):
        reference_string = str(reference)
        asset_id = f"asset_product_reference_{index}_{_slug(Path(reference_string).stem)}"
        reference_asset_ids.append(asset_id)
        # asset:// is deliberately a logical URI. The runtime entrypoint binds
        # it to a public CDN/object-storage URL before calling a real provider.
        assets.append({
            "asset_id": asset_id,
            "kind": "product_image",
            "url": f"asset://{reference_string.lstrip('/')}" ,
            "mime_type": "image/*",
        })
    for asset_id in reference_asset_ids:
        asset_id = str(asset_id)
        if not asset_id:
            continue
        assets.append({
            "asset_id": asset_id,
            "kind": "product_image",
            "url": f"asset://{asset_id}",
            "mime_type": "image/*",
        })

    must_show = _flatten_must_show(source.get("must_show"))
    prohibited = [str(item) for item in source.get("prohibited", [])]
    constraints = [str(item) for item in source.get("constraints", [])]
    budget = source.get("budget") or {}
    budget_amount = budget.get("amount", 0)

    canonical = {
        "schema_version": "1.0",
        "job_id": source["project_id"],
        "status": "UPLOADED",
        "created_at": _now(),
        "updated_at": _now(),
        "assets": assets,
        "product": {
            "name": product_source.get("name", "Unnamed product"),
            "brand": source.get("brand", ""),
            "category": product_source.get("category", ""),
            "source_asset_ids": reference_asset_ids,
            "appearance": {
                "location": source.get("location", ""),
                "style": source.get("style", ""),
            },
            "key_selling_points": product_source.get("core_selling_points", []),
            "must_show": must_show,
            "must_avoid": [*prohibited, *constraints],
        },
        "creative_brief": {
            "audience": source["audience"],
            "platform": _platform(str(source["platform"])),
            "duration_seconds": source["duration_seconds"],
            "aspect_ratio": source["aspect_ratio"],
            "tone": source.get("brand_tone", ""),
            "style_pack": source.get("style", ""),
            "language": "en-US",
            "cta": source["cta"],
            "budget_cny": budget_amount,
        },
        "expected_shot_count": source.get("shot_count", 3),
        "cost": {
            "budget_cny": budget_amount,
            "spent_cny": 0,
            "line_items": [],
        },
    }
    return canonical


def load_and_normalize(path: str | Path) -> dict[str, Any]:
    import json

    source_path = Path(path)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    return normalize_brief_v2(source, source_path=str(source_path))
