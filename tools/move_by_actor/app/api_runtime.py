from __future__ import annotations

import subprocess
import time
from pathlib import Path

import requests

from .config import ApiRuntimeOptions


def _is_api_healthy(url: str) -> bool:
    try:
        response = requests.get(url, timeout=3)
    except Exception:
        return False
    return 200 <= response.status_code < 500


def ensure_api_ready(options: ApiRuntimeOptions) -> subprocess.Popen | None:
    if _is_api_healthy(options.healthcheck_url):
        return None

    if not options.auto_start:
        raise RuntimeError(
            f"API is not reachable: {options.healthcheck_url}. "
            "Enable auto_start or start the API manually."
        )

    project_dir = Path(options.project_dir).expanduser().resolve()
    if not project_dir.exists() or not project_dir.is_dir():
        raise RuntimeError(f"Invalid API project directory: {project_dir}")

    process = subprocess.Popen(
        options.start_command,
        cwd=str(project_dir),
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    deadline = time.time() + max(1, options.startup_timeout_sec)
    poll_interval = max(0.2, options.poll_interval_sec)

    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError("API process exited before becoming healthy.")
        if _is_api_healthy(options.healthcheck_url):
            return process
        time.sleep(poll_interval)

    process.terminate()
    raise RuntimeError(
        f"API did not become healthy within {options.startup_timeout_sec}s."
    )
