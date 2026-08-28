"""Run the Mock Graph from Pod 1's Brief v2 file."""

from __future__ import annotations

import json
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from dreampipe.brief_normalizer import load_and_normalize
from dreampipe.contract import validate_job
from dreampipe.mock_graph import build_mock_graph


ROOT = Path(__file__).parent
OUTPUT_PATH = ROOT / "outputs" / "brief-v2-mock.completed.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DreamPipe Mock Graph from a Brief v2 JSON file.")
    parser.add_argument(
        "brief",
        nargs="?",
        default=str(ROOT / "shared" / "schemas" / "brief.schemav2.json"),
        help="Path to Brief v2 JSON (default: current local Brief v2 fixture)",
    )
    parser.add_argument("--output", default=str(OUTPUT_PATH), help="Output path for the completed mock job")
    args = parser.parse_args()

    job = load_and_normalize(args.brief)
    validate_job(job)
    final_state = build_mock_graph().invoke({"job": job, "events": []})
    validate_job(final_state["job"])
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(final_state["job"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Final status: {final_state['job']['status']}")
    print(f"Project ID: {final_state['job']['job_id']}")
    print(f"Output: {output_path}")
    for item in final_state["events"]:
        print(f"- [{item['node']}] {item['message']}")


if __name__ == "__main__":
    main()
