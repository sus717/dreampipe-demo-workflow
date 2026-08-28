"""Real video QA for DreamPipe.

This module deliberately has no heuristic scores or demo fallbacks.  A QA
decision is produced only after frames from the generated video have been
evaluated by a configured vision model.  If video decoding or model evaluation
fails, the pipeline must stop rather than invent a PASS/FAIL result.
"""

from __future__ import annotations

import base64
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


FAILURE_CODES = {
    "PRODUCT_MISSING",
    "PRODUCT_DRIFT",
    "LOGO_DISTORTED",
    "TEXT_GARBLED",
    "STYLE_DRIFT",
    "PROMPT_MISMATCH",
    "LOW_QUALITY",
    "BRAND_RISK",
}
SCORE_NAMES = (
    "product_consistency",
    "logo_accuracy",
    "prompt_alignment",
    "visual_quality",
    "brand_compliance",
)
SCORE_WEIGHTS = {
    "product_consistency": 0.30,
    "logo_accuracy": 0.15,
    "prompt_alignment": 0.20,
    "visual_quality": 0.15,
    "brand_compliance": 0.20,
}
HARD_FAIL_CODES = {"PRODUCT_MISSING", "LOGO_DISTORTED", "TEXT_GARBLED", "BRAND_RISK"}


class VisionQAError(RuntimeError):
    """Raised when a real QA decision cannot be produced."""


class VisionEvaluator(Protocol):
    """A configured multimodal model which returns a JSON QA assessment."""

    def assess(self, *, instruction: str, image_data_urls: list[str]) -> dict[str, Any]: ...


FrameExtractor = Callable[[str, int], list[str]]


@dataclass(frozen=True)
class OpenAICompatibleVisionConfig:
    """Configuration for an OpenAI-compatible multimodal chat endpoint.

    The defaults target Bailian's compatible endpoint, so the existing
    ``BAILIAN_API_KEY`` can be reused.  A different compatible provider can be
    selected solely through environment variables; credentials are never stored
    in the repository.
    """

    api_key: str
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model: str = "qwen-vl-max"
    timeout_seconds: float = 90.0

    @classmethod
    def from_env(cls) -> "OpenAICompatibleVisionConfig":
        api_key = os.getenv("QA_VISION_API_KEY", "").strip() or os.getenv("BAILIAN_API_KEY", "").strip()
        if not api_key:
            raise VisionQAError("QA_VISION_API_KEY (or BAILIAN_API_KEY) is required for real QA.")
        return cls(
            api_key=api_key,
            base_url=os.getenv("QA_VISION_BASE_URL", cls.base_url).rstrip("/"),
            model=os.getenv("QA_VISION_MODEL", cls.model).strip() or cls.model,
            timeout_seconds=float(os.getenv("QA_VISION_TIMEOUT_SECONDS", "90")),
        )


class OpenAICompatibleVisionEvaluator:
    """Calls a real vision model and rejects malformed/non-JSON responses."""

    def __init__(self, config: OpenAICompatibleVisionConfig | None = None):
        self.config = config or OpenAICompatibleVisionConfig.from_env()

    def assess(self, *, instruction: str, image_data_urls: list[str]) -> dict[str, Any]:
        if not image_data_urls:
            raise VisionQAError("Cannot perform QA without decoded video frames.")
        content: list[dict[str, Any]] = [{"type": "text", "text": instruction}]
        content.extend({"type": "image_url", "image_url": {"url": url}} for url in image_data_urls)
        payload = {
            "model": self.config.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": "You are a rigorous video-production QA evaluator. Return only valid JSON.",
                },
                {"role": "user", "content": content},
            ],
        }
        request = Request(
            f"{self.config.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise VisionQAError(f"Vision QA HTTP {exc.code}: {detail[-1000:]}") from exc
        except (URLError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise VisionQAError(f"Vision QA request failed: {exc}") from exc

        try:
            content_value = body["choices"][0]["message"]["content"]
            if isinstance(content_value, list):
                content_value = "".join(str(item.get("text", "")) for item in content_value if isinstance(item, dict))
            assessment = json.loads(content_value)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise VisionQAError("Vision model did not return a valid JSON QA assessment.") from exc
        if not isinstance(assessment, dict):
            raise VisionQAError("Vision model QA assessment must be a JSON object.")
        return assessment


def extract_video_frames(video_url: str, frame_count: int = 3) -> list[str]:
    """Download an actual video and return evenly distributed JPEG data URLs.

    OpenCV is intentionally imported only here: unit tests and prompt-only code
    do not need it, whereas production QA fails clearly if decoding support was
    not installed.
    """
    if not video_url.startswith(("http://", "https://")):
        raise VisionQAError("Real QA requires a completed video at an HTTP(S) URL.")
    if frame_count < 1:
        raise ValueError("frame_count must be positive")
    try:
        import cv2  # type: ignore[import-not-found]
    except ImportError as exc:
        raise VisionQAError("opencv-python-headless is required to decode generated videos for QA.") from exc

    with tempfile.TemporaryDirectory(prefix="dreampipe-qa-") as directory:
        video_path = Path(directory) / "generated.mp4"
        try:
            with urlopen(video_url, timeout=120) as response:
                video_path.write_bytes(response.read())
        except (HTTPError, URLError, OSError) as exc:
            raise VisionQAError(f"Could not download generated video for QA: {exc}") from exc

        capture = cv2.VideoCapture(str(video_path))
        try:
            total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames < 1:
                raise VisionQAError("Generated video has no decodable frames.")
            indexes = sorted({round(index * (total_frames - 1) / max(frame_count - 1, 1)) for index in range(frame_count)})
            frames: list[str] = []
            for index in indexes:
                capture.set(cv2.CAP_PROP_POS_FRAMES, index)
                ok, frame = capture.read()
                if not ok:
                    raise VisionQAError(f"Could not decode video frame {index}.")
                ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
                if not ok:
                    raise VisionQAError(f"Could not encode video frame {index}.")
                frames.append("data:image/jpeg;base64," + base64.b64encode(encoded.tobytes()).decode("ascii"))
            return frames
        finally:
            capture.release()


@dataclass
class RealVideoQAAgent:
    """Evaluates a generation attempt and returns a contract-shaped QA report."""

    evaluator: VisionEvaluator
    frame_extractor: FrameExtractor = extract_video_frames
    frame_count: int = 3
    pass_threshold: float = 85.0
    minimum_dimension_score: float = 80.0

    def evaluate(
        self,
        *,
        job: Mapping[str, Any],
        shot: Mapping[str, Any],
        prompt: Mapping[str, Any],
        result: Mapping[str, Any],
        video_url: str,
    ) -> dict[str, Any]:
        frames = self.frame_extractor(video_url, self.frame_count)
        assessment = self.evaluator.assess(
            instruction=self._instruction(job=job, shot=shot, prompt=prompt),
            image_data_urls=frames,
        )
        scores = self._validated_scores(assessment)
        failures = self._validated_failures(assessment)
        overall = round(sum(scores[name] * SCORE_WEIGHTS[name] for name in SCORE_NAMES), 2)
        status = "PASS" if self._passes(scores, failures, overall) else "FAIL"
        repair_instruction = str(assessment.get("repair_instruction", "")).strip()
        if status == "FAIL" and not repair_instruction:
            raise VisionQAError("Vision QA returned FAIL without a repair_instruction.")

        report: dict[str, Any] = {
            "report_id": f"qa_{result['result_id']}",
            "shot_id": result["shot_id"],
            "result_id": result["result_id"],
            "status": status,
            "scores": {**scores, "overall": overall},
            "failure_codes": failures,
            "repair_instruction": repair_instruction if status == "FAIL" else "",
            "checked_at": _now(),
            "evidence": assessment.get("evidence", []),
            "qa_model": getattr(getattr(self.evaluator, "config", None), "model", "configured-vision-model"),
        }
        return report

    def _instruction(self, *, job: Mapping[str, Any], shot: Mapping[str, Any], prompt: Mapping[str, Any]) -> str:
        bible = job["project_bible"]
        payload = {
            "task": "Evaluate all supplied frames from one generated video shot. Be conservative: report a failure code whenever there is visible evidence.",
            "product": job["product"],
            "project_bible": bible,
            "shot": shot,
            "generation_prompt": {"prompt": prompt["prompt"], "negative_prompt": prompt.get("negative_prompt", "")},
            "scoring": {name: "number 0-100" for name in SCORE_NAMES},
            "allowed_failure_codes": sorted(FAILURE_CODES),
            "response_schema": {
                "scores": {name: "number 0-100" for name in SCORE_NAMES},
                "failure_codes": ["zero or more allowed failure codes"],
                "repair_instruction": "specific prompt constraint; required if failure_codes is not empty",
                "evidence": [{"frame": "first|middle|last", "observation": "visible fact"}],
            },
            "decision_rule": (
                "If any score is below 80, or the weighted result would be below 85, include at least one "
                "failure code and a specific repair instruction. Do not return an optimistic score without evidence."
            ),
        }
        return json.dumps(payload, ensure_ascii=False)

    def _validated_scores(self, assessment: Mapping[str, Any]) -> dict[str, float]:
        raw_scores = assessment.get("scores")
        if not isinstance(raw_scores, Mapping):
            raise VisionQAError("Vision QA response has no scores object.")
        scores: dict[str, float] = {}
        for name in SCORE_NAMES:
            value = raw_scores.get(name)
            if not isinstance(value, (int, float)) or not 0 <= float(value) <= 100:
                raise VisionQAError(f"Vision QA returned invalid {name} score: {value!r}")
            scores[name] = float(value)
        return scores

    def _validated_failures(self, assessment: Mapping[str, Any]) -> list[str]:
        raw_failures = assessment.get("failure_codes", [])
        if not isinstance(raw_failures, list) or not all(isinstance(item, str) for item in raw_failures):
            raise VisionQAError("Vision QA failure_codes must be a string list.")
        unknown = set(raw_failures) - FAILURE_CODES
        if unknown:
            raise VisionQAError(f"Vision QA returned unsupported failure code(s): {', '.join(sorted(unknown))}")
        return list(dict.fromkeys(raw_failures))

    def _passes(self, scores: Mapping[str, float], failures: list[str], overall: float) -> bool:
        return (
            not failures
            and overall >= self.pass_threshold
            and all(value >= self.minimum_dimension_score for value in scores.values())
        )


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
