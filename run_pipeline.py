"""Run the DreamPipe graph with either the zero-cost Mock provider or Bailian."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from dreampipe.adapters import BailianHappyHorseAdapter
from dreampipe.brief_normalizer import load_and_normalize
from dreampipe.contract import validate_job
from dreampipe.mock_graph import build_mock_graph


ROOT = Path(__file__).parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the DreamPipe LangGraph pipeline.")
    parser.add_argument("brief", help="Path to a Brief v2 JSON file")
    parser.add_argument("--provider", choices=["mock", "happyhorse"], default="mock")
    parser.add_argument(
        "--reference-image-url",
        action="append",
        required=False,
        help="Public HTTP(S) URL for each product reference image (required by happyhorse)",
    )
    parser.add_argument("--output", default=str(ROOT / "outputs" / "pipeline.completed.json"))
    args = parser.parse_args()

    job = load_and_normalize(args.brief)
    if args.provider == "happyhorse":
        urls = args.reference_image_url or []
        if not urls:
            parser.error("--reference-image-url is required with --provider happyhorse")
        if len(urls) > len(job["product"]["source_asset_ids"]):
            parser.error("too many --reference-image-url values for the Brief reference images")
        for index, asset_id in enumerate(job["product"]["source_asset_ids"]):
            if index < len(urls):
                asset = next(item for item in job["assets"] if item["asset_id"] == asset_id)
                asset["url"] = urls[index]
                asset["mime_type"] = "image/png"
        provider = BailianHappyHorseAdapter()
    else:
        provider = None

    validate_job(job)
    final_state = build_mock_graph(provider=provider).invoke({"job": job, "events": []})
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
