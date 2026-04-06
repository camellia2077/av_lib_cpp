from __future__ import annotations

from pathlib import Path

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".ts",
    ".iso",
    ".rmvb",
}

IGNORED_FILES = {".ds_store", "thumbs.db", "desktop.ini"}


def is_video(file_path: Path) -> bool:
    return file_path.suffix.lower() in VIDEO_EXTENSIONS


def is_folder_empty_or_junk(folder_path: Path) -> bool:
    for item in folder_path.iterdir():
        if item.is_file() and item.name.lower() in IGNORED_FILES:
            continue
        return False
    return True

