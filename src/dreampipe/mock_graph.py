"""LangGraph-based mock implementation of the DreamPipe production pipeline.

Every node produces contract-shaped data only. Replace a node body with a real
Skill/LLM or provider adapter without changing its input/output boundary.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from dreampipe.adapters.video_provider import VideoProvider
from dreampipe.qa_agent import RealVideoQAAgent, VisionQAError

MAX_GENERATION_ATTEMPTS = 3


class PipelineState(TypedDict):
    job: dict[str, Any]
    events: list[dict[str, str]]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def event(state: PipelineState, node: str, message: str) -> dict[str, Any]:
    """Add a human-readable event while preserving immutable graph updates."""
    return {"events": [*state["events"], {"at": now(), "node": node, "message": message}]}


def update_job(state: PipelineState, node: str, message: str, **changes: Any) -> dict[str, Any]:
    job = deepcopy(state["job"])
    job.update(changes)
    job["updated_at"] = now()
    return {"job": job, **event(state, node, message)}


def analyze_product(state: PipelineState) -> dict[str, Any]:
    product = deepcopy(state["job"]["product"])
    product.setdefault("appearance", {
        "colors": ["from uploaded reference"],
        "materials": ["to be confirmed by vision model"],
        "shape": "to be confirmed by vision model"
    })
    return update_job(state, "analyze_product", "Mock product analysis completed.", status="BRIEF_READY", product=product)


def create_script(state: PipelineState) -> dict[str, Any]:
    product = state["job"]["product"]
    brief = state["job"]["creative_brief"]
    selling_point = product["key_selling_points"][0]
    script = {
        "concept": f"Use a vivid before-and-after moment to make {product['name']} feel immediately desirable.",
        "hook": f"A visual interruption reveals {product['name']} in the first second.",
        "narrative_structure": "hook_benefit_cta",
        "beats": [
            {"beat_id": "beat_01", "purpose": "hook", "description": "Stop the scroll with a product-first visual hook."},
            {"beat_id": "beat_02", "purpose": "benefit", "description": f"Demonstrate {selling_point} through one visible action."},
            {"beat_id": "beat_03", "purpose": "cta", "description": "Hold a clean product hero frame with CTA."}
        ],
        "voiceover": [f"Meet {product['name']}.", selling_point],
        "on_screen_copy": [selling_point, brief["cta"]],
        "cta_copy": brief["cta"]
    }
    return update_job(state, "create_script", "Mock Director script created.", status="SCRIPT_READY", script=script)


def create_project_bible(state: PipelineState) -> dict[str, Any]:
    product = state["job"]["product"]
    if product["source_asset_ids"]:
        invariant = f"Keep the supplied {product['name']} reference assets unchanged."
    else:
        invariant = f"Keep {product['name']} recognizable from the Project Bible and approved reference assets once supplied."
    bible = {
        "visual_theme": {
            "palette": ["brand primary", "warm neutral", "clean white"],
            "lighting": "soft motivated side light with a precise product rim light",
            "lens_character": "clean commercial macro detail with shallow depth of field",
            "film_look": "premium modern product commercial, photorealistic",
            "motion_language": "one product action and one restrained camera move per shot"
        },
        "product_invariants": [
            invariant,
            *product["must_show"]
        ],
        "brand_invariants": ["Only the supplied brand assets may appear."],
        "negative_constraints": [*product["must_avoid"], "no watermark", "no unreadable packaging text", "no extra products"]
    }
    return update_job(state, "create_project_bible", "Mock Cinematic Director project bible created.", status="BIBLE_READY", project_bible=bible)


def create_storyboard(state: PipelineState) -> dict[str, Any]:
    duration = state["job"]["creative_brief"]["duration_seconds"]
    first = max(3, duration // 4)
    second = max(4, duration // 3)
    third = duration - first - second
    shots = [
        {"shot_id": "shot_01", "sequence": 1, "duration_seconds": first, "purpose": "hook", "description": "A tactile macro reveal establishes the product in under one second.", "composition": "macro product close-up", "camera": "slow push-in", "action": "a single detail catches the light", "audio_direction": "one crisp attention cue", "transition": "hard cut", "product_visibility": "hero", "risk_tags": ["TEXT_GARBLED"]},
        {"shot_id": "shot_02", "sequence": 2, "duration_seconds": second, "purpose": "benefit", "description": "The product performs one visible action that proves its lead benefit.", "composition": "medium product demonstration", "camera": "locked camera", "action": "one clear cause-and-effect action", "audio_direction": "subtle product sound", "transition": "match cut", "product_visibility": "hero", "risk_tags": ["PRODUCT_DRIFT"]},
        {"shot_id": "shot_03", "sequence": 3, "duration_seconds": third, "purpose": "cta", "description": "A clean hero product frame leaves space for the final offer and CTA.", "composition": "hero packshot with copy-safe area", "camera": "slow push-in then hold", "action": "background light moves while product remains fixed", "audio_direction": "music resolves", "transition": "fade out", "product_visibility": "hero", "risk_tags": ["LOGO_DISTORTED"]}
    ]
    return update_job(state, "create_storyboard", "Mock AI Video Storyboard created three shots.", status="STORYBOARD_READY", shots=shots)


def compile_prompts(state: PipelineState, provider: VideoProvider | None = None) -> dict[str, Any]:
    job = state["job"]
    product = job["product"]
    asset_ids = product["source_asset_ids"]
    prompts = []
    for shot in job["shots"]:
        prompts.append({
            "prompt_id": f"prompt_{shot['shot_id']}_v1",
            "shot_id": shot["shot_id"],
            "version": 1,
            "target_model": provider.provider_name if provider is not None else "mock-video-provider",
            "generation_mode": "image_to_video",
            "reference_asset_ids": asset_ids,
            "prompt": f"{shot['description']} Camera: {shot['camera']}. Preserve {product['name']} and all Project Bible invariants. {job['project_bible']['visual_theme']['lighting']}. {shot['duration_seconds']} seconds.",
            "negative_prompt": "; ".join(job["project_bible"]["negative_constraints"]),
            "parameters": {"duration_seconds": shot["duration_seconds"], "aspect_ratio": job["creative_brief"]["aspect_ratio"]}
        })
    return update_job(state, "compile_prompts", "Mock MX Shell Prompt compiler created provider prompts.", status="PROMPTS_READY", generation_prompts=prompts)


def latest_reports(job: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for report in job.get("qa_reports", []):
        reports[report["shot_id"]] = report
    return reports


def latest_results(job: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for result in job.get("generation_results", []):
        results[result["shot_id"]] = result
    return results


def generate_shots(state: PipelineState, provider: VideoProvider | None = None) -> dict[str, Any]:
    job = deepcopy(state["job"])
    reports = latest_reports(job)
    results = latest_results(job)
    targets = []
    for shot in job["shots"]:
        shot_id = shot["shot_id"]
        report = reports.get(shot_id)
        if report is None:
            targets.append(shot_id)
        elif report["status"] == "FAIL" and results[shot_id]["attempt"] < MAX_GENERATION_ATTEMPTS:
            targets.append(shot_id)

    for shot_id in targets:
        prompts = [p for p in job["generation_prompts"] if p["shot_id"] == shot_id]
        prompt = prompts[-1]
        attempt = results[shot_id]["attempt"] + 1 if shot_id in results else 1
        asset_id = f"asset_{shot_id}_attempt_{attempt}"
        provider_result: dict[str, Any] | None = None
        try:
            if provider is not None:
                if not prompt["reference_asset_ids"]:
                    raise ValueError("Provider generation requires at least one approved reference asset URL.")
                reference_asset_id = prompt["reference_asset_ids"][0]
                reference_asset = next(
                    (asset for asset in job["assets"] if asset["asset_id"] == reference_asset_id),
                    None,
                )
                if not reference_asset or not str(reference_asset.get("url", "")).startswith(("http://", "https://")):
                    raise ValueError(
                        f"Provider generation requires an accessible HTTP(S) reference asset URL: {reference_asset_id}"
                    )
                provider_result = provider.submit_generation(
                    prompt=prompt["prompt"],
                    image_url=reference_asset["url"],
                    parameters={
                        "duration_seconds": next(s["duration_seconds"] for s in job["shots"] if s["shot_id"] == shot_id),
                        "aspect_ratio": job["creative_brief"]["aspect_ratio"],
                    },
                )
                if provider_result.get("status") != "SUCCEEDED":
                    wait_for_completion = getattr(provider, "wait_for_completion", None)
                    if wait_for_completion is None:
                        raise RuntimeError(
                            "Video provider returned an asynchronous task but does not implement wait_for_completion()."
                        )
                    provider_result = wait_for_completion(provider_result["task_id"])
        except Exception as exc:
            job["status"] = "FAILED"
            job["error"] = {
                "code": "VIDEO_PROVIDER_ERROR",
                "message": str(exc),
                "shot_id": shot_id,
                "provider": provider.provider_name if provider is not None else "mock-video-provider",
            }
            job["updated_at"] = now()
            return {"job": job, **event(state, "generate_shots", f"Video generation failed for {shot_id}: {exc}")}
        if provider is not None:
            output_url = (provider_result or {}).get("asset_urls", [None])[0]
        else:
            output_url = f"https://mock-assets.dreampipe.local/{job['job_id']}/{asset_id}.mp4"
        provider_name = provider_result.get("provider", "mock-video-provider") if provider_result else "mock-video-provider"
        provider_task_id = provider_result.get("task_id", f"mock_task_{shot_id}_{attempt}") if provider_result else f"mock_task_{shot_id}_{attempt}"
        generation_status = provider_result.get("status", "SUCCEEDED") if provider_result else "SUCCEEDED"
        if generation_status != "SUCCEEDED" or not output_url:
            raise RuntimeError(f"Video provider did not return a completed video for shot {shot_id}")
        job["assets"].append({
            "asset_id": asset_id,
            "kind": "video",
            "url": output_url,
            "mime_type": "video/mp4",
            "source_shot_id": shot_id,
            "duration_seconds": next(s["duration_seconds"] for s in job["shots"] if s["shot_id"] == shot_id)
        })
        job.setdefault("generation_results", []).append({
            "result_id": f"result_{shot_id}_attempt_{attempt}",
            "shot_id": shot_id,
            "prompt_id": prompt["prompt_id"],
            "attempt": attempt,
            "status": generation_status,
            "provider": provider_name,
            "provider_task_id": provider_task_id,
            "output_asset_id": asset_id,
            "created_at": now(),
            "completed_at": now()
        })
    job["status"] = "QA_CHECKING"
    job["updated_at"] = now()
    provider_label = provider.provider_name if provider is not None else "mock provider"
    return {"job": job, **event(state, "generate_shots", f"{provider_label} generated {len(targets)} shot(s).")}


def qa_shots(state: PipelineState) -> dict[str, Any]:
    job = deepcopy(state["job"])
    reviewed_result_ids = {report["result_id"] for report in job.get("qa_reports", [])}
    new_reports = []
    for result in job.get("generation_results", []):
        if result["result_id"] in reviewed_result_ids:
            continue
        # The intentional first failure proves the repair loop during every demo run.
        is_first_shot_02_attempt = result["shot_id"] == "shot_02" and result["attempt"] == 1
        status: Literal["PASS", "FAIL"] = "FAIL" if is_first_shot_02_attempt else "PASS"
        scores = {
            "product_consistency": 72 if status == "FAIL" else 96,
            "logo_accuracy": 93 if status == "FAIL" else 98,
            "prompt_alignment": 78 if status == "FAIL" else 94,
            "visual_quality": 84 if status == "FAIL" else 93,
            "brand_compliance": 98,
            "overall": 78 if status == "FAIL" else 95
        }
        new_reports.append({
            "report_id": f"qa_{result['result_id']}",
            "shot_id": result["shot_id"],
            "result_id": result["result_id"],
            "status": status,
            "scores": scores,
            "failure_codes": ["PRODUCT_DRIFT"] if status == "FAIL" else [],
            "repair_instruction": "Lock the supplied product reference, preserve its silhouette and regenerate only this shot." if status == "FAIL" else "",
            "checked_at": now()
        })
    job.setdefault("qa_reports", []).extend(new_reports)
    all_reports = latest_reports(job)
    failed = [shot_id for shot_id, report in all_reports.items() if report["status"] == "FAIL"]
    job["status"] = "RETRYING" if failed else "ASSEMBLING"
    job["updated_at"] = now()
    return {"job": job, **event(state, "qa_shots", f"Mock QA evaluated {len(new_reports)} result(s); failed shots: {', '.join(failed) or 'none'}.")}


def real_qa_shots(state: PipelineState, qa_agent: RealVideoQAAgent) -> dict[str, Any]:
    """Evaluate only unreviewed real generation attempts; never manufacture scores."""
    job = deepcopy(state["job"])
    reviewed_result_ids = {report["result_id"] for report in job.get("qa_reports", [])}
    reports: list[dict[str, Any]] = []
    try:
        for result in job.get("generation_results", []):
            if result["result_id"] in reviewed_result_ids:
                continue
            asset = next(
                (item for item in job["assets"] if item["asset_id"] == result["output_asset_id"]),
                None,
            )
            prompt = next(
                (item for item in job["generation_prompts"] if item["prompt_id"] == result["prompt_id"]),
                None,
            )
            shot = next((item for item in job["shots"] if item["shot_id"] == result["shot_id"]), None)
            if not asset or not prompt or not shot:
                raise VisionQAError(f"QA inputs are incomplete for result {result['result_id']}.")
            reports.append(qa_agent.evaluate(
                job=job,
                shot=shot,
                prompt=prompt,
                result=result,
                video_url=asset["url"],
            ))
    except Exception as exc:
        job["status"] = "FAILED"
        job["error"] = {"code": "VISION_QA_ERROR", "message": str(exc)}
        job["updated_at"] = now()
        return {"job": job, **event(state, "real_qa_shots", f"Real vision QA failed: {exc}")}

    job.setdefault("qa_reports", []).extend(reports)
    failed = [report["shot_id"] for report in latest_reports(job).values() if report["status"] == "FAIL"]
    job["status"] = "RETRYING" if failed else "ASSEMBLING"
    job["updated_at"] = now()
    return {"job": job, **event(state, "real_qa_shots", f"Real vision QA evaluated {len(reports)} result(s); failed shots: {', '.join(failed) or 'none'}.")}


def finish_failed_job(state: PipelineState) -> dict[str, Any]:
    job = deepcopy(state["job"])
    if job["status"] != "FAILED":
        failed_shots = [
            report["shot_id"]
            for report in latest_reports(job).values()
            if report["status"] == "FAIL"
        ]
        job["status"] = "FAILED"
        job["error"] = {
            "code": "QA_RETRY_EXHAUSTED",
            "message": "Real QA did not pass after the allowed retry attempts.",
            "shot_ids": failed_shots,
        }
        job["updated_at"] = now()
    return {"job": job, **event(state, "finish_failed_job", "Pipeline stopped because generation or real QA could not produce a passing shot.")}


def route_after_generation(state: PipelineState) -> Literal["qa_shots", "finish_failed_job"]:
    return "finish_failed_job" if state["job"]["status"] == "FAILED" else "qa_shots"


def route_after_qa(state: PipelineState) -> Literal["repair_prompts", "assemble_video", "finish_failed_job"]:
    if state["job"]["status"] == "FAILED":
        return "finish_failed_job"
    reports = latest_reports(state["job"])
    results = latest_results(state["job"])
    retryable = [shot_id for shot_id, report in reports.items() if report["status"] == "FAIL" and results[shot_id]["attempt"] < MAX_GENERATION_ATTEMPTS]
    if retryable:
        return "repair_prompts"
    if any(report["status"] == "FAIL" for report in reports.values()):
        return "finish_failed_job"
    return "assemble_video"


def repair_prompts(state: PipelineState) -> dict[str, Any]:
    job = deepcopy(state["job"])
    reports = latest_reports(job)
    prompts = list(job["generation_prompts"])
    for shot_id, report in reports.items():
        if report["status"] != "FAIL":
            continue
        latest = [p for p in prompts if p["shot_id"] == shot_id][-1]
        repaired = deepcopy(latest)
        repaired["version"] += 1
        repaired["prompt_id"] = f"prompt_{shot_id}_v{repaired['version']}"
        repaired["prompt"] = f"{latest['prompt']} Repair constraint: {report['repair_instruction']}"
        prompts.append(repaired)
    job["generation_prompts"] = prompts
    job["status"] = "GENERATING"
    job["updated_at"] = now()
    return {"job": job, **event(state, "repair_prompts", "Mock repair agent created a new prompt version for failed shots.")}


def assemble_video(state: PipelineState) -> dict[str, Any]:
    job = deepcopy(state["job"])
    reports = latest_reports(job)
    results = latest_results(job)
    video_asset_ids = [results[shot["shot_id"]]["output_asset_id"] for shot in job["shots"] if reports[shot["shot_id"]]["status"] == "PASS"]
    final_asset_id = "asset_final_ad"
    job["assets"].append({
        "asset_id": final_asset_id,
        "kind": "video",
        "url": f"https://mock-assets.dreampipe.local/{job['job_id']}/{final_asset_id}.mp4",
        "mime_type": "video/mp4",
        "duration_seconds": job["creative_brief"]["duration_seconds"]
    })
    job["render_manifest"] = {
        "composition_id": "product_ad_vertical_v1",
        "video_asset_ids": video_asset_ids,
        "audio_asset_ids": [],
        "output_aspect_ratio": job["creative_brief"]["aspect_ratio"],
        "output_asset_id": final_asset_id
    }
    job["cost"]["spent_cny"] = 8.4
    job["cost"]["line_items"] = [
        {"category": "llm", "amount_cny": 0.4},
        {"category": "video", "amount_cny": 8.0}
    ]
    job["status"] = "COMPLETED"
    job["updated_at"] = now()
    return {"job": job, **event(state, "assemble_video", "Mock Remotion assembler created the final MP4 manifest.")}


def build_mock_graph(provider: VideoProvider | None = None):
    graph = StateGraph(PipelineState)
    graph.add_node("analyze_product", analyze_product)
    graph.add_node("create_script", create_script)
    graph.add_node("create_project_bible", create_project_bible)
    graph.add_node("create_storyboard", create_storyboard)
    graph.add_node("compile_prompts", lambda state: compile_prompts(state, provider=provider))
    graph.add_node("generate_shots", lambda state: generate_shots(state, provider=provider))
    graph.add_node("qa_shots", qa_shots)
    graph.add_node("repair_prompts", repair_prompts)
    graph.add_node("assemble_video", assemble_video)
    graph.add_node("finish_failed_job", finish_failed_job)
    graph.add_edge(START, "analyze_product")
    graph.add_edge("analyze_product", "create_script")
    graph.add_edge("create_script", "create_project_bible")
    graph.add_edge("create_project_bible", "create_storyboard")
    graph.add_edge("create_storyboard", "compile_prompts")
    graph.add_edge("compile_prompts", "generate_shots")
    graph.add_conditional_edges(
        "generate_shots",
        route_after_generation,
        {"qa_shots": "qa_shots", "finish_failed_job": "finish_failed_job"},
    )
    graph.add_conditional_edges("qa_shots", route_after_qa, {"repair_prompts": "repair_prompts", "assemble_video": "assemble_video"})
    graph.add_edge("repair_prompts", "generate_shots")
    graph.add_edge("assemble_video", END)
    graph.add_edge("finish_failed_job", END)
    return graph.compile()


def build_real_graph(*, provider: VideoProvider, qa_agent: RealVideoQAAgent):
    """Build the production path; both video generation and QA are mandatory."""
    graph = StateGraph(PipelineState)
    graph.add_node("analyze_product", analyze_product)
    graph.add_node("create_script", create_script)
    graph.add_node("create_project_bible", create_project_bible)
    graph.add_node("create_storyboard", create_storyboard)
    graph.add_node("compile_prompts", lambda state: compile_prompts(state, provider=provider))
    graph.add_node("generate_shots", lambda state: generate_shots(state, provider=provider))
    graph.add_node("qa_shots", lambda state: real_qa_shots(state, qa_agent=qa_agent))
    graph.add_node("repair_prompts", repair_prompts)
    graph.add_node("assemble_video", assemble_video)
    graph.add_node("finish_failed_job", finish_failed_job)
    graph.add_edge(START, "analyze_product")
    graph.add_edge("analyze_product", "create_script")
    graph.add_edge("create_script", "create_project_bible")
    graph.add_edge("create_project_bible", "create_storyboard")
    graph.add_edge("create_storyboard", "compile_prompts")
    graph.add_edge("compile_prompts", "generate_shots")
    graph.add_conditional_edges(
        "generate_shots",
        route_after_generation,
        {"qa_shots": "qa_shots", "finish_failed_job": "finish_failed_job"},
    )
    graph.add_conditional_edges(
        "qa_shots",
        route_after_qa,
        {
            "repair_prompts": "repair_prompts",
            "assemble_video": "assemble_video",
            "finish_failed_job": "finish_failed_job",
        },
    )
    graph.add_edge("repair_prompts", "generate_shots")
    graph.add_edge("assemble_video", END)
    graph.add_edge("finish_failed_job", END)
    return graph.compile()
