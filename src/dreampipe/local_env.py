"""Minimal local ``.env`` loader for development credentials.

The file is deliberately local-only and ignored by Git. Existing environment
variables always win, so deployment platforms can supply credentials normally.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_local_env(path: str | Path) -> None:
    """Load simple ``KEY=VALUE`` pairs without overriding existing variables."""
    env_path = Path(path)
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)
