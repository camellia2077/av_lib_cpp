from __future__ import annotations

import os
from pathlib import Path

from ..move_by_actor.app.scanner import VIDEO_EXTENSIONS
from .models import MetadataFailure


def _is_video(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def collect_video_files(input_path: Path) -> tuple[list[Path], list[MetadataFailure]]:
    files: list[Path] = []
    failures: list[MetadataFailure] = []

    if input_path.is_file():
        if _is_video(input_path):
            return [input_path.resolve()], []
        failures.append(
            MetadataFailure(
                file_path=str(input_path.resolve()),
                reason="INVALID_INPUT",
                message=f"Input file is not a supported video: {input_path.name}",
            )
        )
        return files, failures

    if input_path.is_dir():
        for dirpath_str, _dirnames, filenames in os.walk(input_path):
            dirpath = Path(dirpath_str)
            for name in filenames:
                candidate = dirpath / name
                if _is_video(candidate):
                    files.append(candidate.resolve())
        files.sort(key=lambda path: str(path).lower())
        return files, failures

    failures.append(
        MetadataFailure(
            file_path=str(input_path),
            reason="INVALID_INPUT",
            message="Input path is neither a file nor a directory.",
        )
    )
    return files, failures

