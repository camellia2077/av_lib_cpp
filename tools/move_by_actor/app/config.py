from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    api_base: str = "http://127.0.0.1:3000/api"
    timeout: int = 20
    use_env_proxy: bool = True


@dataclass
class ApiRuntimeOptions:
    auto_start: bool = False
    project_dir: str = ""
    start_command: str = "npm start"
    healthcheck_url: str = "http://127.0.0.1:3000/"
    startup_timeout_sec: int = 60
    poll_interval_sec: float = 1.0
    stop_on_exit: bool = False


@dataclass
class RuntimeConfigFile:
    api: ApiRuntimeOptions


def default_runtime_config_path() -> Path:
    return Path(__file__).resolve().parent.parent / "runtime.toml"
