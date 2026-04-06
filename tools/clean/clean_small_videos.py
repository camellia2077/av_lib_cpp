from __future__ import annotations

import argparse
import os
from pathlib import Path
# This is a simple utility to find and optionally delete small video files (e.g. <50MB) in a directory tree.
VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".ts",
    ".m4v",
}

MB = 1024 * 1024


def iter_small_videos(root: Path, threshold_bytes: int) -> list[tuple[Path, int]]:
    matched: list[tuple[Path, int]] = []
    for dirpath_str, _, filenames in os.walk(root):
        if not filenames:
            continue
        dirpath = Path(dirpath_str)
        for name in filenames:
            suffix = Path(name).suffix.lower()
            if suffix not in VIDEO_EXTENSIONS:
                continue
            file_path = dirpath / name
            try:
                size = file_path.stat().st_size
            except OSError:
                continue
            if size < threshold_bytes:
                matched.append((file_path, size))
    return matched


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan a directory and find/delete videos smaller than threshold."
    )
    parser.add_argument("input_dir", help="Directory to scan recursively")
    parser.add_argument(
        "--threshold-mb",
        type=int,
        default=50,
        help="Size threshold in MB (default: 50)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete matched files (default is preview only)",
    )
    args = parser.parse_args()

    root = Path(args.input_dir).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Invalid directory: {root}")
    if args.threshold_mb <= 0:
        raise SystemExit("--threshold-mb must be > 0")

    threshold_bytes = args.threshold_mb * MB
    matched = iter_small_videos(root, threshold_bytes)

    mode = "DELETE" if args.delete else "PREVIEW"
    print(f"[{mode}] threshold={args.threshold_mb}MB, matched={len(matched)}")

    deleted = 0
    for path, size in matched:
        size_mb = size / MB
        print(f"{size_mb:8.2f} MB | {path}")
        if args.delete:
            try:
                path.unlink()
                deleted += 1
            except OSError as exc:
                print(f"FAILED to delete: {path} ({exc})")

    if args.delete:
        print(f"Deleted: {deleted}/{len(matched)}")


if __name__ == "__main__":
    main()
