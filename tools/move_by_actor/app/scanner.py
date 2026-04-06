from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".ts",
    ".m4v",
    ".mpg",
    ".mpeg",
    ".m2ts",
    ".mts",
    ".rmvb",
    ".vob",
    ".webm",
    ".3gp",
    ".asf",
    ".f4v",
}
HYPHENATED_CODE_PATTERN = re.compile(r"([A-Za-z]{2,10})-(\d{2,6})")
COMPACT_CODE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z]{2,10})(\d{2,6})(?![A-Za-z0-9])",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ScanItem:
    path: Path
    is_dir: bool
    code_hint: str | None


def extract_movie_code(stem: str) -> str | None:
    matched = HYPHENATED_CODE_PATTERN.search(stem)
    if matched:
        return f"{matched.group(1).upper()}-{matched.group(2)}"

    compact = COMPACT_CODE_PATTERN.search(stem)
    if compact:
        return f"{compact.group(1).upper()}-{compact.group(2)}"

    return None


def _video_files_in_directory(dirpath: Path, filenames: list[str]) -> list[Path]:
    files: list[Path] = []
    for name in filenames:
        if Path(name).suffix.lower() in VIDEO_EXTENSIONS:
            files.append(dirpath / name)
    return files


def _first_video_code_in_dir(dirpath: Path, filenames: list[str]) -> str | None:
    for name in sorted(filenames):
        if Path(name).suffix.lower() not in VIDEO_EXTENSIONS:
            continue
        code = extract_movie_code(Path(name).stem)
        if code:
            return code
    return None


def scan_items_for_move(input_dir: Path, recursive: bool) -> list[ScanItem]:
    items: list[ScanItem] = []
    if recursive:
        for dirpath_str, dirnames, filenames in os.walk(input_dir, topdown=True):
            dirpath = Path(dirpath_str)
            video_files = _video_files_in_directory(dirpath, filenames)
            if not video_files:
                continue

            if dirpath != input_dir:
                # Recursive mode uses "video folder as move unit":
                # when a folder contains videos, move this folder once.
                # Prefer folder-name code (e.g. "MIZD-374"), then fallback to
                # the first video filename code inside that folder.
                code_hint = extract_movie_code(dirpath.name)
                if not code_hint:
                    code_hint = _first_video_code_in_dir(dirpath, filenames)
                items.append(ScanItem(path=dirpath, is_dir=True, code_hint=code_hint))
                # Parent folder is already selected, no need to descend.
                dirnames[:] = []
                continue

            for file_path in sorted(video_files, key=lambda p: p.name.lower()):
                items.append(
                    ScanItem(
                        path=file_path,
                        is_dir=False,
                        code_hint=extract_movie_code(file_path.stem),
                    )
                )
    else:
        for entry in input_dir.iterdir():
            if entry.is_file() and entry.suffix.lower() in VIDEO_EXTENSIONS:
                items.append(
                    ScanItem(
                        path=entry,
                        is_dir=False,
                        code_hint=extract_movie_code(entry.stem),
                    )
                )
    return sorted(items, key=lambda item: item.path.name.lower())
