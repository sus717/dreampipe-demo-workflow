"""Run the Mock Graph from Pod 1's Brief file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dreampipe.brief_normalizer import load_and_normalize
from dreampipe.contract import validate_job
from dreampipe.mock_graph import build_mock_graph


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DreamPipe Mock Graph from a Brief JSON file.")
    parser.add_argument("brief", nargs="?", default=str(ROOT / "shared" / "brief.json"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "brief-v2-mock.completed.json"))
    args = parser.parse_args()
    job = load_and_normalize(args.brief)
    validate_job(job)
    final_state = build_mock_graph().invoke({"job": job, "events": []})
    validate_job(final_state["job"])
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(final_state["job"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Final status: {final_state['job']['status']}")


if __name__ == "__main__":
    main()
