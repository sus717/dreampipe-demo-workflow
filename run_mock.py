"""Run the complete DreamPipe LangGraph mock workflow.

Usage: python run_mock.py
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from dreampipe.contract import validate_job
from dreampipe.mock_graph import build_mock_graph


ROOT = Path(__file__).parent
INPUT_PATH = ROOT / "examples" / "mock-job.input.json"
OUTPUT_PATH = ROOT / "outputs" / "mock-job.completed.json"


def main() -> None:
    job = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    validate_job(job)
    graph = build_mock_graph()
    final_state = graph.invoke({"job": job, "events": []})
    validate_job(final_state["job"])
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(final_state["job"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Final status: {final_state['job']['status']}")
    print(f"Events: {len(final_state['events'])}")
    print(f"Output: {OUTPUT_PATH}")
    for item in final_state["events"]:
        print(f"- [{item['node']}] {item['message']}")


if __name__ == "__main__":
    main()
