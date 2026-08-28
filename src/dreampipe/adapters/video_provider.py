"""Provider protocol shared by LangGraph generation nodes."""

from __future__ import annotations

from typing import Any, Mapping, Protocol


class VideoProvider(Protocol):
    provider_name: str

    def submit_generation(
        self,
        *,
        prompt: str,
        image_url: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]: ...

    def get_generation_status(self, task_id: str) -> dict[str, Any]: ...

    def get_generation_output(self, task_id: str) -> dict[str, Any]: ...
