"""Run DreamPipe with real video generation and real vision QA only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from dreampipe.adapters import BailianHappyHorseAdapter
from dreampipe.brief_normalizer import load_and_normalize
from dreampipe.contract import validate_job
from dreampipe.mock_graph import build_real_graph
from dreampipe.qa_agent import OpenAICompatibleVisionEvaluator, RealVideoQAAgent


ROOT = Path(__file__).parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run real DreamPipe generation, QA and retry.")
    parser.add_argument("brief", help="Path to a Brief v2 JSON file")
    parser.add_argument(
        "--reference-image-url",
        action="append",
        required=True,
        help="Public HTTP(S) URL for each product reference image",
    )
    parser.add_argument("--output", default=str(ROOT / "outputs" / "real-pipeline.completed.json"))
    args = parser.parse_args()

    job = load_and_normalize(args.brief)
    source_ids = job["product"]["source_asset_ids"]
    if len(args.reference_image_url) != len(source_ids):
        parser.error("Provide exactly one --reference-image-url for every Brief reference image.")
    for asset_id, url in zip(source_ids, args.reference_image_url, strict=True):
        if not url.startswith(("http://", "https://")):
            parser.error("--reference-image-url values must be public HTTP(S) URLs.")
        asset = next(item for item in job["assets"] if item["asset_id"] == asset_id)
        asset["url"] = url
        asset["mime_type"] = "image/png"

    provider = BailianHappyHorseAdapter()
    qa_agent = RealVideoQAAgent(evaluator=OpenAICompatibleVisionEvaluator())
    validate_job(job)
    final_state = build_real_graph(provider=provider, qa_agent=qa_agent).invoke({"job": job, "events": []})
    validate_job(final_state["job"])
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(final_state["job"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Final status: {final_state['job']['status']}")
    print(f"Output: {output_path}")
    for item in final_state["events"]:
        print(f"- [{item['node']}] {item['message']}")


if __name__ == "__main__":
    main()
