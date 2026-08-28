"""GLM-4.5-Air adapter for structured prompt compilation and repair."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_GLM_MODEL = "glm-4.5-air"
DEFAULT_GLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"


class GLMError(RuntimeError):
    """Raised for a rejected or malformed GLM response."""


@dataclass(frozen=True)
class GLMConfig:
    api_key: str = ""
    base_url: str = DEFAULT_GLM_BASE_URL
    model: str = DEFAULT_GLM_MODEL
    timeout_seconds: float = 90.0

    @classmethod
    def from_env(cls) -> "GLMConfig":
        return cls(
            api_key=os.getenv("GLM_API_KEY", "").strip(),
            base_url=os.getenv("GLM_BASE_URL", DEFAULT_GLM_BASE_URL).strip().rstrip("/"),
            model=os.getenv("GLM_MODEL", DEFAULT_GLM_MODEL).strip() or DEFAULT_GLM_MODEL,
            timeout_seconds=float(os.getenv("GLM_TIMEOUT_SECONDS", "90")),
        )

    @property
    def chat_url(self) -> str:
        return f"{self.base_url}/chat/completions"


class GLMAdapter:
    provider_name = DEFAULT_GLM_MODEL

    def __init__(self, config: GLMConfig | None = None):
        self.config = config or GLMConfig.from_env()

    def chat_json(self, messages: Sequence[Mapping[str, Any]], *, temperature: float = 0.2) -> dict[str, Any]:
        if not self.config.api_key:
            raise GLMError("GLM_API_KEY is required for GLM prompt compilation.")
        payload = {
            "model": self.config.model,
            "messages": [dict(message) for message in messages],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        request = Request(
            self.config.chat_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            value = json.loads(content)
        except HTTPError as exc:
            raise GLMError(f"GLM HTTP {exc.code}") from exc
        except (URLError, KeyError, IndexError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GLMError(f"GLM request failed: {exc}") from exc
        if not isinstance(value, dict):
            raise GLMError("GLM JSON response must be an object")
        return value


class GLMPromptCompiler:
    """Convert Pod 2's model-agnostic shot into a HappyHorse prompt."""

    def __init__(self, client: GLMAdapter | None = None):
        self.client = client or GLMAdapter()

    def _request(self, task: str, payload: Mapping[str, Any]) -> dict[str, str]:
        result = self.client.chat_json([
            {"role": "system", "content": "You are a strict cinematic prompt compiler. Return only JSON with prompt and negative_prompt. Preserve all constraints; never invent logos, products, official endorsement, or readable in-video text."},
            {"role": "user", "content": json.dumps({"task": task, **payload, "output_contract": {"prompt": "string", "negative_prompt": "string"}}, ensure_ascii=False)},
        ], temperature=0.2)
        prompt = result.get("prompt")
        negative_prompt = result.get("negative_prompt", "")
        if not isinstance(prompt, str) or not prompt.strip() or not isinstance(negative_prompt, str):
            raise GLMError("GLM prompt compiler returned an invalid prompt contract")
        return {"prompt": prompt.strip(), "negative_prompt": negative_prompt.strip()}

    def compile(self, *, shot: Mapping[str, Any], project_bible: Mapping[str, Any], brief: Mapping[str, Any], target_model: str) -> dict[str, str]:
        return self._request("Compile a provider-specific image-to-video prompt.", {"target_model": target_model, "brief": brief, "project_bible": project_bible, "shot": shot})

    def repair(self, *, shot: Mapping[str, Any], project_bible: Mapping[str, Any], brief: Mapping[str, Any], target_model: str, previous_prompt: Mapping[str, Any], repair_instruction: str) -> dict[str, str]:
        return self._request("Repair only the failed constraint in the previous prompt.", {"target_model": target_model, "brief": brief, "project_bible": project_bible, "shot": shot, "previous_prompt": previous_prompt, "repair_instruction": repair_instruction})
