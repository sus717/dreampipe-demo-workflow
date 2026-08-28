"""Alibaba Cloud Bailian adapter for HappyHorse-1.1-I2V.

The adapter only talks to the public DashScope-compatible asynchronous API. It
does not read or persist credentials; the API key must be supplied through
``BAILIAN_API_KEY`` (or passed explicitly by the application).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_MODEL = "happyhorse-1.1-i2v"
DEFAULT_REGION = "cn-beijing"


class BailianHappyHorseError(RuntimeError):
    """Raised when the Bailian API rejects a request or returns bad data."""


@dataclass(frozen=True)
class BailianHappyHorseConfig:
    """Runtime configuration for the HappyHorse provider.

    ``workspace_id`` is optional because some deployments expose the global
    DashScope endpoint. When present, the regional workspace endpoint from the
    model page is used.
    """

    api_key: str = ""
    workspace_id: str = ""
    region: str = DEFAULT_REGION
    model: str = DEFAULT_MODEL
    synthesis_base_url: str = ""
    task_base_url: str = ""
    timeout_seconds: float = 60.0

    @classmethod
    def from_env(cls) -> "BailianHappyHorseConfig":
        workspace_id = os.getenv("BAILIAN_WORKSPACE_ID", "").strip()
        region = os.getenv("BAILIAN_REGION", DEFAULT_REGION).strip() or DEFAULT_REGION
        synthesis_base_url = os.getenv("BAILIAN_SYNTHESIS_BASE_URL", "").strip()
        task_base_url = os.getenv("BAILIAN_TASK_BASE_URL", "").strip()
        return cls(
            api_key=os.getenv("BAILIAN_API_KEY", "").strip(),
            workspace_id=workspace_id,
            region=region,
            model=os.getenv("BAILIAN_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL,
            synthesis_base_url=synthesis_base_url,
            task_base_url=task_base_url,
            timeout_seconds=float(os.getenv("BAILIAN_TIMEOUT_SECONDS", "60")),
        )

    @property
    def synthesis_url(self) -> str:
        if self.synthesis_base_url:
            return self.synthesis_base_url.rstrip("/")
        if self.workspace_id:
            return f"https://{self.workspace_id}.{self.region}.maas.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
        return "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"

    @property
    def task_url_base(self) -> str:
        if self.task_base_url:
            return self.task_base_url.rstrip("/")
        if self.workspace_id:
            return f"https://{self.workspace_id}.{self.region}.maas.aliyuncs.com/api/v1/tasks"
        return "https://dashscope.aliyuncs.com/api/v1/tasks"


def _json_response(response: Any) -> dict[str, Any]:
    try:
        value = json.loads(response.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BailianHappyHorseError("Bailian returned a non-JSON response") from exc
    if not isinstance(value, dict):
        raise BailianHappyHorseError("Bailian returned a JSON value that is not an object")
    return value


class BailianHappyHorseAdapter:
    """Stable provider boundary used by the LangGraph generation node."""

    provider_name = DEFAULT_MODEL

    def __init__(self, config: BailianHappyHorseConfig | None = None):
        self.config = config or BailianHappyHorseConfig.from_env()

    def _headers(self) -> dict[str, str]:
        if not self.config.api_key:
            raise BailianHappyHorseError(
                "BAILIAN_API_KEY is required for real HappyHorse generation; "
                "use the mock provider when no key is configured."
            )
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, url: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = self._headers()
        if method == "POST":
            headers["X-DashScope-Async"] = "enable"
        request = Request(url, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                return _json_response(response)
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise BailianHappyHorseError(f"Bailian HTTP {exc.code}: {details[-2000:]}") from exc
        except URLError as exc:
            raise BailianHappyHorseError(f"Cannot reach Bailian API: {exc.reason}") from exc

    def build_synthesis_payload(
        self,
        *,
        prompt: str,
        image_url: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")
        if not image_url.startswith(("http://", "https://")):
            raise ValueError("image_url must be an http(s) URL accessible by Bailian")
        values = dict(parameters or {})
        resolution = str(values.get("resolution", "720P"))
        duration = int(values.get("duration", values.get("duration_seconds", 5)))
        if duration <= 0:
            raise ValueError("duration must be a positive integer")
        return {
            "model": self.config.model,
            "input": {
                "prompt": prompt,
                "media": [{"type": "first_frame", "url": image_url}],
            },
            "parameters": {"resolution": resolution, "duration": duration},
        }

    def submit_generation(
        self,
        *,
        prompt: str,
        image_url: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = self.build_synthesis_payload(prompt=prompt, image_url=image_url, parameters=parameters)
        response = self._request("POST", self.config.synthesis_url, payload)
        output = response.get("output") or {}
        task_id = output.get("task_id") or response.get("task_id")
        if not task_id:
            raise BailianHappyHorseError(f"Bailian response did not contain output.task_id: {response}")
        task_status = output.get("task_status") or "PENDING"
        return {
            "provider": self.provider_name,
            "task_id": str(task_id),
            "status": _normalize_status(task_status),
            "request_id": response.get("request_id"),
            "raw": response,
        }

    def get_generation_status(self, task_id: str) -> dict[str, Any]:
        if not task_id:
            raise ValueError("task_id must not be empty")
        response = self._request("GET", f"{self.config.task_url_base}/{task_id}")
        output = response.get("output") or {}
        status = _normalize_status(output.get("task_status") or response.get("task_status"))
        urls = _video_urls(response)
        return {
            "provider": self.provider_name,
            "task_id": task_id,
            "status": status,
            "progress_percent": output.get("progress") or output.get("progress_percent"),
            "asset_urls": urls,
            "failure_reason": output.get("message") or output.get("code") or response.get("message"),
            "raw": response,
        }

    def get_generation_output(self, task_id: str) -> dict[str, Any]:
        status = self.get_generation_status(task_id)
        if status["status"] != "SUCCEEDED":
            raise BailianHappyHorseError(f"Generation is not complete for {task_id}: {status['status']}")
        if not status["asset_urls"]:
            raise BailianHappyHorseError(f"Bailian task {task_id} succeeded without a video URL")
        return {
            "provider": self.provider_name,
            "task_id": task_id,
            "asset_urls": status["asset_urls"],
            "raw": status["raw"],
        }

    def wait_for_completion(
        self,
        task_id: str,
        *,
        poll_interval_seconds: float = 2.0,
        timeout_seconds: float | None = None,
    ) -> dict[str, Any]:
        """Poll an async task until it succeeds or fails."""
        deadline = time.monotonic() + (timeout_seconds or self.config.timeout_seconds)
        while True:
            status = self.get_generation_status(task_id)
            if status["status"] in {"SUCCEEDED", "FAILED"}:
                if status["status"] == "FAILED":
                    raise BailianHappyHorseError(
                        f"HappyHorse task {task_id} failed: {status.get('failure_reason') or 'unknown error'}"
                    )
                return self.get_generation_output(task_id)
            if time.monotonic() >= deadline:
                raise BailianHappyHorseError(f"Timed out waiting for HappyHorse task {task_id}")
            time.sleep(max(0.1, poll_interval_seconds))


def _normalize_status(value: Any) -> str:
    normalized = str(value or "UNKNOWN").upper()
    return {
        "PENDING": "QUEUED",
        "QUEUED": "QUEUED",
        "RUNNING": "RUNNING",
        "PROCESSING": "RUNNING",
        "SUCCEEDED": "SUCCEEDED",
        "SUCCESS": "SUCCEEDED",
        "FAILED": "FAILED",
        "FAIL": "FAILED",
        "CANCELED": "FAILED",
        "CANCELLED": "FAILED",
    }.get(normalized, "UNKNOWN")


def _video_urls(payload: Mapping[str, Any]) -> list[str]:
    output = payload.get("output") or {}
    candidates: list[Any] = [
        output.get("video_url"),
        output.get("video_urls"),
        output.get("url"),
        output.get("urls"),
        (output.get("results") or {}).get("video_url") if isinstance(output.get("results"), Mapping) else None,
    ]
    urls: list[str] = []
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.startswith(("http://", "https://")):
            urls.append(candidate)
        elif isinstance(candidate, list):
            urls.extend(item for item in candidate if isinstance(item, str) and item.startswith(("http://", "https://")))
    return list(dict.fromkeys(urls))
