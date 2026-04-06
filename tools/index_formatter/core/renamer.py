from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .engine import sanitize_stem_with_meta

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
SINGLE_LETTER_PART_PATTERN = re.compile(r"^([A-Z]{2,10}-\d{2,6})-([A-Z])$")
ANSI_RED = "\x1b[31m"
ANSI_YELLOW = "\x1b[33m"
ANSI_RESET = "\x1b[0m"
ColorMode = Literal["auto", "always", "never"]


@dataclass(frozen=True)
class RenameCandidate:
    name: str
    stem: str
    suffix: str
    sanitized_stem: str
    expected_match: bool


@dataclass(frozen=True)
class PreviewMessage:
    source_name: str
    target_name: str
    expected_match: bool

    @property
    def text(self) -> str:
        return f"{self.source_name} -> {self.target_name}\n"


def is_video(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def unique_target_name(target_name: str, reserved_names: set[str]) -> str:
    if target_name.lower() not in reserved_names:
        return target_name

    base, suffix = os.path.splitext(target_name)
    index = 1
    while True:
        candidate = f"{base}-{index}{suffix}"
        if candidate.lower() not in reserved_names:
            return candidate
        index += 1


def _should_colorize(mode: ColorMode) -> bool:
    if mode == "always":
        return True
    if mode == "never":
        return False
    return sys.stdout.isatty()


def _render_preview_message(message: PreviewMessage, color_enabled: bool) -> str:
    # Preview coloring semantics:
    # - Yellow: stem was normalized by a deterministic rule (parser/special-case).
    # - Red: stem came from fallback cleanup (non-structured match).
    line = message.text
    if not color_enabled:
        return line
    if message.expected_match:
        return f"{ANSI_YELLOW}{line}{ANSI_RESET}"
    return f"{ANSI_RED}{line}{ANSI_RESET}"


def _split_base_and_letter_part(stem: str) -> tuple[str, str] | None:
    matched = SINGLE_LETTER_PART_PATTERN.fullmatch(stem)
    if not matched:
        return None
    return matched.group(1), matched.group(2)


def _build_preview_message(
    source_name: str, target_name: str, expected_match: bool
) -> PreviewMessage:
    return PreviewMessage(
        source_name=source_name,
        target_name=target_name,
        expected_match=expected_match,
    )


def apply_directory_context_rules(
    candidates: list[RenameCandidate],
) -> list[RenameCandidate]:
    adjusted_stems: list[str] = [candidate.sanitized_stem for candidate in candidates]
    base_to_indexes: dict[str, list[int]] = defaultdict(list)

    for index, candidate in enumerate(candidates):
        split = _split_base_and_letter_part(candidate.sanitized_stem)
        if not split:
            continue
        base_code, _ = split
        base_to_indexes[base_code].append(index)

    for base_code, indexes in base_to_indexes.items():
        # Why use "same base group size" instead of "directory video count":
        # A folder can contain multiple unrelated videos. We only drop the
        # trailing part letter when exactly one file belongs to this base code.
        # This avoids corrupting true multi-part sets like MVSD-344-A/B.
        if len(indexes) == 1:
            adjusted_stems[indexes[0]] = base_code

    # For duplicate sanitized base names produced from multiple raw files in the
    # same directory, assign deterministic numeric suffixes starting at 1.
    # Only include entries that actually need renaming so already-canonical files
    # are not unexpectedly renamed.
    duplicate_base_to_indexes: dict[str, list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        adjusted = adjusted_stems[index]
        if candidate.stem == adjusted:
            continue
        duplicate_base_to_indexes[adjusted].append(index)

    for base_code, indexes in duplicate_base_to_indexes.items():
        if len(indexes) <= 1:
            continue
        for order, idx in enumerate(indexes, start=1):
            adjusted_stems[idx] = f"{base_code}-{order}"

    return [
        RenameCandidate(
            name=candidates[i].name,
            stem=candidates[i].stem,
            suffix=candidates[i].suffix,
            sanitized_stem=adjusted_stems[i],
            expected_match=candidates[i].expected_match,
        )
        for i in range(len(candidates))
    ]


def process(
    root: Path,
    apply_changes: bool,
    quiet: bool = False,
    color: ColorMode = "auto",
) -> tuple[int, int]:
    scanned = 0
    renamed = 0
    # Colors are a preview-only aid; apply mode stays plain for predictable logs.
    color_enabled = (not apply_changes) and (not quiet) and _should_colorize(color)
    for dirpath_str, dirnames, filenames in os.walk(root):
        if not filenames:
            continue

        # Use one directory scan result for both video filtering and collision
        # reservation to avoid extra per-directory filesystem traversal.
        reserved_names = {name.lower() for name in filenames}
        reserved_names.update(name.lower() for name in dirnames)
        video_names = [
            name
            for name in filenames
            if os.path.splitext(name)[1].lower() in VIDEO_EXTENSIONS
        ]
        if not video_names:
            continue

        candidates = []
        for name in sorted(video_names):
            stem, suffix = os.path.splitext(name)
            result = sanitize_stem_with_meta(stem)
            candidates.append(
                RenameCandidate(
                    name=name,
                    stem=stem,
                    suffix=suffix,
                    sanitized_stem=result.value,
                    # Yellow means a deterministic parse/special-case match.
                    # Red is reserved for fallback-cleaned outputs.
                    expected_match=not result.used_fallback,
                )
            )
        candidates = apply_directory_context_rules(candidates)
        dirpath = Path(dirpath_str)

        for candidate in candidates:
            scanned += 1
            new_stem = candidate.sanitized_stem
            if new_stem == candidate.stem:
                continue

            target_name = new_stem + candidate.suffix
            same_logical_path = candidate.name.lower() == target_name.lower()
            if not same_logical_path:
                target_name = unique_target_name(target_name, reserved_names)
                reserved_names.discard(candidate.name.lower())
                reserved_names.add(target_name.lower())

            if not quiet:
                message = _build_preview_message(
                    source_name=candidate.name,
                    target_name=target_name,
                    expected_match=candidate.expected_match,
                )
                output = _render_preview_message(
                    message=message,
                    color_enabled=color_enabled,
                )
                print(output)
            if apply_changes:
                source_path = dirpath / candidate.name
                target_path = dirpath / target_name
                source_path.rename(target_path)
            renamed += 1

    return scanned, renamed
