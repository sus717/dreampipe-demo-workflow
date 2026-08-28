"""Run DreamPipe with real HappyHorse generation and real vision QA."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dreampipe.adapters import BailianHappyHorseAdapter, GLMAdapter, GLMPromptCompiler
from dreampipe.brief_normalizer import load_and_normalize
from dreampipe.contract import validate_job
from dreampipe.creative_handoff import load_creative_handoff
from dreampipe.local_env import load_local_env
from dreampipe.mock_graph import build_real_graph
from dreampipe.qa_agent import OpenAICompatibleVisionEvaluator, RealVideoQAAgent


def main() -> None:
    load_local_env(ROOT / ".env")
    parser = argparse.ArgumentParser(description="Run real DreamPipe generation, QA and retry.")
    parser.add_argument("brief", help="Path to a Brief JSON file")
    parser.add_argument("--reference-image-url", action="append", required=True, help="Public HTTP(S) URL for each product reference image")
    parser.add_argument(
        "--creative-source",
        choices=["pod2", "mock"],
        default="pod2",
        help="Use Pod 2's frozen creative handoff (default) or legacy Mock creative nodes.",
    )
    parser.add_argument("--llm", choices=["mock", "glm"], default="glm", help="Prompt compiler: GLM-4.5-Air (default) or Mock.")
    parser.add_argument("--output", default=str(ROOT / "outputs" / "real-pipeline.completed.json"))
    args = parser.parse_args()
    job = load_and_normalize(args.brief)
    source_ids = job["product"]["source_asset_ids"]
    if len(args.reference_image_url) != len(source_ids):
        parser.error("Provide exactly one --reference-image-url for every Brief reference image.")
    for asset_id, url in zip(source_ids, args.reference_image_url, strict=True):
        if not url.startswith(("http://", "https://")):
            parser.error("--reference-image-url values must be public HTTP(S) URLs.")
        next(asset for asset in job["assets"] if asset["asset_id"] == asset_id).update(url=url, mime_type="image/png")
    validate_job(job)
    creative_handoff = load_creative_handoff(job) if args.creative_source == "pod2" else None
    prompt_compiler = GLMPromptCompiler(GLMAdapter()) if args.llm == "glm" else None
    final_state = build_real_graph(
        provider=BailianHappyHorseAdapter(),
        qa_agent=RealVideoQAAgent(evaluator=OpenAICompatibleVisionEvaluator()),
        creative_handoff=creative_handoff,
        prompt_compiler=prompt_compiler,
    ).invoke({"job": job, "events": []})
    validate_job(final_state["job"])
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(final_state["job"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Final status: {final_state['job']['status']}")


if __name__ == "__main__":
    main()
