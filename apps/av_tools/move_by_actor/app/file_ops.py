from __future__ import annotations

import re
from pathlib import Path

WINDOWS_FORBIDDEN_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*]+')


def sanitize_actor_dir_name(actor_name: str) -> str:
    cleaned = WINDOWS_FORBIDDEN_CHARS_PATTERN.sub("_", actor_name).strip().strip(".")
    return cleaned or "UNKNOWN_ACTOR"


def unique_target_path(target: Path) -> Path:
    if not target.exists():
        return target
    base = target.stem
    suffix = target.suffix
    parent = target.parent
    index = 1
    while True:
        candidate = parent / f"{base}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1
