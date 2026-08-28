from __future__ import annotations

import unittest
from pathlib import Path

from dreampipe.adapters.bailian_happyhorse_adapter import (
    BailianHappyHorseAdapter,
    BailianHappyHorseConfig,
)
from dreampipe.brief_normalizer import load_and_normalize
from dreampipe.mock_graph import build_mock_graph


class FakeHappyHorseAdapter(BailianHappyHorseAdapter):
    def __init__(self, responses):
        super().__init__(BailianHappyHorseConfig(api_key="test-key"))
        self.responses = iter(responses)
        self.requests = []

    def _request(self, method, url, payload=None):
        self.requests.append((method, url, payload))
        return next(self.responses)


class ImmediateProvider:
    provider_name = "happyhorse-1.1-i2v"

    def submit_generation(self, *, prompt, image_url, parameters=None):
        return {"provider": self.provider_name, "task_id": "task", "status": "SUCCEEDED", "asset_urls": ["https://example.com/out.mp4"]}


class HappyHorseAdapterTests(unittest.TestCase):
    def test_payload_matches_bailian_example(self):
        adapter = BailianHappyHorseAdapter(BailianHappyHorseConfig(api_key="test-key"))
        payload = adapter.build_synthesis_payload(
            prompt="一只猫在草地上奔跑",
            image_url="https://example.com/product.png",
            parameters={"resolution": "720P", "duration_seconds": 5, "aspect_ratio": "9:16"},
        )
        self.assertEqual(payload["model"], "happyhorse-1.1-i2v")
        self.assertEqual(payload["input"]["media"], [{"type": "first_frame", "url": "https://example.com/product.png"}])
        self.assertEqual(payload["parameters"], {"resolution": "720P", "duration": 5})

    def test_submit_and_status_are_normalized(self):
        adapter = FakeHappyHorseAdapter([
            {"output": {"task_id": "task-1", "task_status": "PENDING"}, "request_id": "req-1"},
            {"output": {"task_status": "SUCCEEDED", "video_url": "https://example.com/out.mp4"}},
        ])
        submitted = adapter.submit_generation(prompt="p", image_url="https://example.com/in.png")
        self.assertEqual(submitted["status"], "QUEUED")
        status = adapter.get_generation_status("task-1")
        self.assertEqual(status["status"], "SUCCEEDED")
        self.assertEqual(status["asset_urls"], ["https://example.com/out.mp4"])
        self.assertEqual(adapter.requests[0][0], "POST")
        self.assertEqual(adapter.requests[1][0], "GET")

    def test_provider_is_injected_into_langgraph_generation_node(self):
        root = Path(__file__).resolve().parents[1]
        brief_path = root / "shared" / "brief.json"
        if not brief_path.is_file():
            brief_path = root / "shared" / "schemas" / "brief.schemav2.json"
        job = load_and_normalize(brief_path)
        for asset in job["assets"]:
            asset["url"] = "https://example.com/product.png"
        final_state = build_mock_graph(provider=ImmediateProvider()).invoke({"job": job, "events": []})
        self.assertEqual(final_state["job"]["status"], "COMPLETED")
        self.assertTrue(all(result["provider"] == "happyhorse-1.1-i2v" for result in final_state["job"]["generation_results"]))


if __name__ == "__main__":
    unittest.main()
