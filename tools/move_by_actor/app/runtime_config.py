from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError as exc:
    raise RuntimeError("Python 3.11+ is required for TOML support.") from exc

from .config import ApiRuntimeOptions, RuntimeConfigFile


def _as_bool(value: Any, default: bool) -> bool:
    return bool(value) if isinstance(value, bool) else default


def _as_str(value: Any, default: str) -> str:
    return str(value) if isinstance(value, str) else default


def _as_int(value: Any, default: int) -> int:
    return int(value) if isinstance(value, int) else default


def _as_float(value: Any, default: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default


def load_runtime_config(
    path: Path, defaults: RuntimeConfigFile
) -> RuntimeConfigFile:
    if not path.exists():
        return defaults

    with path.open("rb") as f:
        data = tomllib.load(f)

    api = data.get("api", {})
    if not isinstance(api, dict):
        return defaults

    parsed_api = ApiRuntimeOptions(
        auto_start=_as_bool(api.get("auto_start"), defaults.api.auto_start),
        project_dir=_as_str(api.get("project_dir"), defaults.api.project_dir),
        start_command=_as_str(api.get("start_command"), defaults.api.start_command),
        healthcheck_url=_as_str(
            api.get("healthcheck_url"), defaults.api.healthcheck_url
        ),
        startup_timeout_sec=_as_int(
            api.get("startup_timeout_sec"), defaults.api.startup_timeout_sec
        ),
        poll_interval_sec=_as_float(
            api.get("poll_interval_sec"), defaults.api.poll_interval_sec
        ),
        stop_on_exit=_as_bool(api.get("stop_on_exit"), defaults.api.stop_on_exit),
    )
    return RuntimeConfigFile(api=parsed_api)
