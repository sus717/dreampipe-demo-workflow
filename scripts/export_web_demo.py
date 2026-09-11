"""Build offline web snapshots from the shared contracts and real Mock graph.

No model calls, credentials or real videos are involved. Synthetic reference
assets exist only in this export; the approved Brief remains unchanged.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jsonschema import Draft202012Validator
from dreampipe.brief_normalizer import load_and_normalize
from dreampipe.contract import validate_job
from dreampipe.creative_handoff import load_creative_handoff
from dreampipe.mock_graph import build_mock_graph
from dreampipe.status_view import build_pipeline_status


def build_demo() -> dict:
    job = load_and_normalize(ROOT / "shared/brief.json")
    handoff = load_creative_handoff(job)
    graph = build_mock_graph(creative_handoff=handoff)
    waiting = graph.invoke({"job": job, "events": []})
    # Explicit, export-only fixtures. The Mock provider never fetches this URL.
    job["product"]["source_asset_ids"] = ["offline_demo_reference"]
    job["assets"] = [{"asset_id": "offline_demo_reference", "kind": "product_image",
                      "url": "https://example.invalid/offline-demo.png", "mime_type": "image/png"}]
    phases = {"waiting": waiting}
    for state in graph.stream({"job": job, "events": []}, stream_mode="values"):
        node = state["events"][-1]["node"] if state["events"] else ""
        if node == "generate_shots" and "running" not in phases:
            phases["running"] = state
        if state["job"]["status"] == "RETRYING":
            phases["retrying"] = state
        if state["job"]["status"] == "COMPLETED":
            phases["completed"] = state
    if set(phases) != {"waiting", "running", "retrying", "completed"}:
        raise RuntimeError("Integrated demo must exercise asset gate, generation, retry and completion.")
    schema = json.loads((ROOT / "shared/schemas/pipeline_status.schema.json").read_text(encoding="utf-8"))
    snapshots = {}
    for phase, state in phases.items():
        validate_job(state["job"])
        status = build_pipeline_status(state["job"], state["events"])
        Draft202012Validator(schema).validate(status)
        # Mock URLs are not playable outputs and must never become playback links.
        status["final_output"] = {"status": "PENDING"}
        snapshots[phase] = {"status": status, "events": state["events"], "cost": state["job"]["cost"]}
    return {"mode": "offline-mock", "has_real_video": False,
            "project_id": job["job_id"], "snapshots": snapshots}


if __name__ == "__main__":
    target = ROOT / "web/src/data/pipelineDemo.generated.json"
    target.write_text(json.dumps(build_demo(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Exported four validated offline snapshots to {target.relative_to(ROOT)}")
