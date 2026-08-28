"""LibTV CLI adapter for DreamPipe video generation.

This module intentionally shells out to the official `libtv` executable. It
does not call LibTV HTTP endpoints or depend on personal `.libtv` state.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any, Sequence


DEFAULT_LIBTV_BIN = r"C:\Users\27389\.libtv\libtv.exe"


class LibTVError(RuntimeError):
    """Raised when the LibTV CLI exits unsuccessfully or returns invalid JSON."""


@dataclass(frozen=True)
class LibTVConfig:
    executable: str = os.environ.get("LIBTV_BIN", DEFAULT_LIBTV_BIN)
    project_uuid: str = os.environ.get("LIBTV_PROJECT_UUID", "")
    default_model: str = "Wan 3.0"


def _parse_json(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        return {}
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    # Be tolerant of CLI progress lines around the final JSON object.
    for line in reversed(text.splitlines()):
        candidate = line.strip()
        if not (candidate.startswith("{") and candidate.endswith("}")):
            continue
        try:
            value = json.loads(candidate)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            continue
    raise LibTVError(f"LibTV returned non-JSON output: {text[-1000:]}")


class LibTVAdapter:
    """Small provider adapter with stable methods for the LangGraph node."""

    def __init__(self, config: LibTVConfig | None = None):
        self.config = config or LibTVConfig()

    def _project(self) -> str:
        if not self.config.project_uuid:
            raise LibTVError("LIBTV_PROJECT_UUID is required; do not hardcode a personal LibTV canvas ID.")
        return self.config.project_uuid

    def _run(self, args: Sequence[str]) -> dict[str, Any]:
        command = [self.config.executable, *args]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
        except OSError as exc:
            raise LibTVError(f"Cannot execute LibTV CLI at {self.config.executable}: {exc}") from exc
        if completed.returncode != 0:
            details = (completed.stderr or completed.stdout).strip()
            raise LibTVError(f"LibTV command failed ({completed.returncode}): {details[-2000:]}")
        return _parse_json(completed.stdout)

    def list_nodes(self) -> dict[str, Any]:
        return self._run(["node", "list", "-p", self._project()])

    def upload_asset(self, name: str, local_path: str | Path, *, media_type: str | None = None) -> dict[str, Any]:
        args = ["upload", name, "-p", self._project(), "--resource", str(local_path)]
        if media_type:
            args.extend(["--type", media_type])
        return self._run(args)

    def build_generation_command(
        self,
        *,
        node_name: str,
        prompt: str,
        reference_nodes: Sequence[str] = (),
        parameters: dict[str, Any] | None = None,
        run: bool = True,
    ) -> list[str]:
        parameters = dict(parameters or {})
        mode_type = parameters.pop("modeType", None) or ("mixed2video" if reference_nodes else "text2video")
        model = parameters.pop("model", self.config.default_model)
        ratio = parameters.pop("ratio", "9:16")
        resolution = parameters.pop("resolution", "720P")
        duration = parameters.pop("duration", 5)
        enable_sound = parameters.pop("enableSound", "off")
        extend_prompt = parameters.pop("extendPrompt", 0)
        count = parameters.pop("count", 1)
        args = [
            "node", "create", node_name,
            "-p", self._project(),
            "-t", "video",
            "-s", f"model={model}",
            "-s", f"modeType={mode_type}",
            "-s", f"ratio={ratio}",
            "-s", f"resolution={resolution}",
            "-s", f"duration={duration}",
            "-s", f"enableSound={enable_sound}",
            "-s", f"extendPrompt={extend_prompt}",
            "-s", f"count={count}",
            "--prompt", prompt,
        ]
        for node in reference_nodes:
            args.extend(["--left", node])
        if run:
            args.append("--run")
        for key, value in parameters.items():
            args.extend(["-s", f"{key}={value}"])
        return args

    def submit_generation(
        self,
        *,
        node_name: str,
        prompt: str,
        reference_nodes: Sequence[str] = (),
        parameters: dict[str, Any] | None = None,
        run: bool = True,
    ) -> dict[str, Any]:
        return self._run(self.build_generation_command(
            node_name=node_name,
            prompt=prompt,
            reference_nodes=reference_nodes,
            parameters=parameters,
            run=run,
        ))

    def get_generation_status(self, node: str) -> dict[str, Any]:
        payload = self._run(["node", node, "-p", self._project()])
        task_info = payload.get("taskInfo") or payload.get("data", {}).get("taskInfo") or {}
        data = payload.get("data") or {}
        urls = data.get("url") or []
        if urls:
            status = "SUCCEEDED"
        elif task_info.get("loading"):
            status = "RUNNING"
        elif task_info.get("status") in (3, "3"):
            status = "FAILED"
        else:
            status = "UNKNOWN"
        return {
            "provider": "libtv",
            "node_key": payload.get("nodeKey", node),
            "node_name": payload.get("name") or data.get("name"),
            "status": status,
            "task_id": task_info.get("taskId"),
            "progress_percent": task_info.get("progressPercent"),
            "urls": urls,
            "poster": data.get("poster"),
            "raw": payload,
        }

    def get_generation_output(self, node: str) -> dict[str, Any]:
        status = self.get_generation_status(node)
        if status["status"] != "SUCCEEDED":
            raise LibTVError(f"Generation is not complete for {node}: {status['status']}")
        return {
            "asset_urls": status["urls"],
            "poster": status["poster"],
            "node_key": status["node_key"],
            "provider": "libtv",
        }
