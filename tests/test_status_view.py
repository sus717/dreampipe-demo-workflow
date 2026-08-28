from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

from dreampipe.brief_normalizer import load_and_normalize
from dreampipe.mock_graph import build_mock_graph
from dreampipe.status_view import build_pipeline_status


ROOT = Path(__file__).resolve().parents[1]


class PipelineStatusViewTests(unittest.TestCase):
    def test_missing_reference_assets_projects_to_frontend_contract(self):
        brief = ROOT / "shared" / "brief.json"
        if not brief.is_file():
            brief = ROOT / "shared" / "schemas" / "brief.schemav2.json"
        job = load_and_normalize(brief)
        state = build_mock_graph().invoke({"job": job, "events": []})
        status = build_pipeline_status(state["job"], state["events"])
        schema = json.loads((ROOT / "shared" / "schemas" / "pipeline_status.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(status)
        self.assertEqual(status["status"], "WAITING_FOR_ASSETS")
        self.assertEqual(status["current_step"], "awaiting_assets")
        self.assertEqual(status["error"]["code"], "REFERENCE_ASSETS_REQUIRED")
        self.assertEqual(status["final_output"]["status"], "PENDING")

    def test_failed_job_keeps_error_safe_for_frontend(self):
        job = {
            "job_id": "demo-1",
            "status": "FAILED",
            "updated_at": "2026-08-28T15:32:00Z",
            "creative_brief": {"duration_seconds": 15, "aspect_ratio": "9:16"},
            "shots": [{"shot_id": "S01"}],
            "assets": [],
            "error": {"code": "VIDEO_PROVIDER_ERROR", "message": "Timed out", "shot_id": "S01"},
        }
        status = build_pipeline_status(job, [{"node": "generate_shots"}])
        self.assertEqual(status["error"]["code"], "VIDEO_PROVIDER_ERROR")
        self.assertTrue(status["error"]["retryable"])
        self.assertEqual(status["final_output"], {"status": "FAILED"})


if __name__ == "__main__":
    unittest.main()
