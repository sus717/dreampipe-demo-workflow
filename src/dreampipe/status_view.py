"""Project a LangGraph job into the stable frontend status contract."""

from __future__ import annotations

from typing import Any, Mapping


MAX_ATTEMPTS = 3
PROGRESS_STEPS = {
    "analyze_product", "ensure_reference_assets", "create_script",
    "create_project_bible", "create_storyboard", "compile_prompts",
    "generate_shots", "qa_shots", "assemble_video",
}
TOTAL_STEPS = len(PROGRESS_STEPS)
STEP_MAP = {
    "analyze_product": "analyze_product",
    "ensure_reference_assets": "ensure_reference_assets",
    "finish_waiting_for_assets": "awaiting_assets",
    "create_script": "create_script",
    "create_project_bible": "create_project_bible",
    "create_storyboard": "create_storyboard",
    "compile_prompts": "compile_prompts",
    "generate_shots": "generate_shots",
    "qa_shots": "qa_shots",
    "repair_prompts": "repair_prompts",
    "assemble_video": "assemble_video",
    "finish_failed_job": "failed",
}


def _latest_by_shot(items: list[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for item in items:
        shot_id = str(item.get("shot_id", ""))
        if shot_id:
            result[shot_id] = item
    return result


def _current_step(job: Mapping[str, Any], events: list[Mapping[str, Any]]) -> str:
    if job.get("status") == "COMPLETED":
        return "completed"
    if job.get("status") == "FAILED":
        return "failed"
    if job.get("status") == "CANCELLED":
        return "cancelled"
    if job.get("status") == "WAITING_FOR_ASSETS":
        return "awaiting_assets"
    if events:
        return STEP_MAP.get(str(events[-1].get("node", "")), "brief_normalize")
    return "brief_normalize"


def _public_status(job_status: str) -> str:
    return {
        "COMPLETED": "SUCCEEDED",
        "FAILED": "FAILED",
        "CANCELLED": "CANCELLED",
        "WAITING_FOR_ASSETS": "WAITING_FOR_ASSETS",
        "RETRYING": "RETRYING",
        "UPLOADED": "QUEUED",
    }.get(job_status, "RUNNING")


def build_pipeline_status(job: Mapping[str, Any], events: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Return only frontend-safe, display-oriented state; never include secrets."""
    reports = _latest_by_shot(list(job.get("qa_reports", [])))
    results = _latest_by_shot(list(job.get("generation_results", [])))
    retry_shots = []
    qa_shots = []
    passed = failed = pending = 0
    for shot in job.get("shots", []):
        shot_id = str(shot["shot_id"])
        result = results.get(shot_id)
        report = reports.get(shot_id)
        if report is None:
            qa_status = "PENDING"
            pending += 1
        else:
            qa_status = str(report["status"])
            if qa_status == "PASS":
                passed += 1
            else:
                failed += 1
        qa_shots.append({
            "shot_id": shot_id,
            "status": qa_status,
            "scores": dict(report.get("scores", {})) if report else {},
            "failure_codes": list(report.get("failure_codes", [])) if report else [],
            "repair_instruction": str(report.get("repair_instruction", "")) if report else "",
            "checked_at": report.get("checked_at") if report else None,
        })
        attempt = int(result.get("attempt", 0)) if result else 0
        retrying = bool(report and report.get("status") == "FAIL" and attempt < MAX_ATTEMPTS)
        retry_shots.append({
            "shot_id": shot_id,
            "attempt": max(1, attempt),
            "status": "RETRYING" if retrying else ("PASSED" if qa_status == "PASS" else "PENDING"),
            "repair_instruction": str(report.get("repair_instruction", "")) if retrying else "",
        })

    current_step = _current_step(job, events)
    completed_steps = len({event.get("node") for event in events} & PROGRESS_STEPS)
    public_status = _public_status(str(job["status"]))
    output_asset_id = (job.get("render_manifest") or {}).get("output_asset_id")
    output_asset = next((asset for asset in job.get("assets", []) if asset.get("asset_id") == output_asset_id), None)
    final_output = None
    if public_status == "SUCCEEDED" and output_asset:
        final_output = {
            "status": "READY",
            "video_url": output_asset["url"],
            "duration_seconds": output_asset.get("duration_seconds", job["creative_brief"]["duration_seconds"]),
            "aspect_ratio": job["creative_brief"]["aspect_ratio"],
        }
    elif public_status == "FAILED":
        final_output = {"status": "FAILED"}
    else:
        final_output = {"status": "PENDING"}

    raw_error = job.get("error")
    error = None
    if raw_error:
        error = {
            "code": str(raw_error.get("code", "PIPELINE_ERROR")),
            "message": str(raw_error.get("message", "Pipeline failed.")),
            "step": current_step,
            "retryable": raw_error.get("code") in {"VIDEO_PROVIDER_ERROR", "REFERENCE_ASSETS_REQUIRED"},
        }
        if raw_error.get("shot_id"):
            error["shot_id"] = raw_error["shot_id"]
    return {
        "schema_version": "1.0",
        "project_id": job["job_id"],
        "status": public_status,
        "current_step": current_step,
        "progress": {"completed_steps": completed_steps, "total_steps": TOTAL_STEPS, "percent": 100 if public_status == "SUCCEEDED" else int(completed_steps / TOTAL_STEPS * 100)},
        "retry": {"is_retrying": any(item["status"] == "RETRYING" for item in retry_shots), "max_attempts": MAX_ATTEMPTS, "shots": retry_shots},
        "qa": {"summary": {"passed": passed, "failed": failed, "pending": pending}, "shots": qa_shots},
        "error": error,
        "final_output": final_output,
        "updated_at": job["updated_at"],
    }
