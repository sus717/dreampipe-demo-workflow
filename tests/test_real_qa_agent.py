from __future__ import annotations

import unittest

from dreampipe.qa_agent import RealVideoQAAgent, VisionQAError


class StaticEvaluator:
    def __init__(self, assessment):
        self.assessment = assessment

    def assess(self, *, instruction, image_data_urls):
        self.instruction = instruction
        self.image_data_urls = image_data_urls
        return self.assessment


def frames(_url, _count):
    return ["data:image/jpeg;base64,ZmFrZQ=="]


def inputs():
    return {
        "job": {
            "product": {"name": "测试饮料"},
            "project_bible": {"product_invariants": ["包装不可改变"]},
        },
        "shot": {"shot_id": "shot_01", "description": "产品特写"},
        "prompt": {"prompt_id": "prompt_shot_01_v1", "prompt": "产品特写"},
        "result": {"result_id": "result_shot_01_attempt_1", "shot_id": "shot_01"},
    }


class RealVideoQAAgentTests(unittest.TestCase):
    def test_pass_uses_real_model_scores(self):
        evaluator = StaticEvaluator({
            "scores": {
                "product_consistency": 96,
                "logo_accuracy": 94,
                "prompt_alignment": 90,
                "visual_quality": 92,
                "brand_compliance": 95,
            },
            "failure_codes": [],
            "repair_instruction": "",
            "evidence": [{"frame": "middle", "observation": "product shape matches reference"}],
        })
        report = RealVideoQAAgent(evaluator=evaluator, frame_extractor=frames).evaluate(
            **inputs(), video_url="https://example.com/generated.mp4"
        )
        self.assertEqual(report["status"], "PASS")
        # Weighted score from qa_agent.SCORE_WEIGHTS:
        # 96*.30 + 94*.15 + 90*.20 + 92*.15 + 95*.20 = 93.70.
        self.assertEqual(report["scores"]["overall"], 93.70)
        self.assertIn("project_bible", evaluator.instruction)

    def test_fail_requires_specific_real_repair_instruction(self):
        evaluator = StaticEvaluator({
            "scores": {
                "product_consistency": 58,
                "logo_accuracy": 92,
                "prompt_alignment": 72,
                "visual_quality": 88,
                "brand_compliance": 96,
            },
            "failure_codes": ["PRODUCT_DRIFT", "PROMPT_MISMATCH"],
            "repair_instruction": "Use the supplied product image as the locked first frame; keep the can silhouette unchanged.",
            "evidence": [{"frame": "last", "observation": "can silhouette differs from reference"}],
        })
        report = RealVideoQAAgent(evaluator=evaluator, frame_extractor=frames).evaluate(
            **inputs(), video_url="https://example.com/generated.mp4"
        )
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["failure_codes"], ["PRODUCT_DRIFT", "PROMPT_MISMATCH"])
        self.assertIn("locked first frame", report["repair_instruction"])

    def test_invalid_model_output_fails_closed(self):
        evaluator = StaticEvaluator({
            "scores": {"product_consistency": 110},
            "failure_codes": [],
        })
        with self.assertRaises(VisionQAError):
            RealVideoQAAgent(evaluator=evaluator, frame_extractor=frames).evaluate(
                **inputs(), video_url="https://example.com/generated.mp4"
            )


if __name__ == "__main__":
    unittest.main()
