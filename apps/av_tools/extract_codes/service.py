from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..fetch_metadata.parser import extract_standard_movie_code
from ..fetch_metadata.scanner import collect_video_files


@dataclass(frozen=True)
class RawCodeEntry:
    source: str
    raw_value: str


def _extract_raw_value_from_json_item(item: Any, index: int) -> RawCodeEntry | None:
    if isinstance(item, str):
        return RawCodeEntry(source=f"json[{index}]", raw_value=item)
    if isinstance(item, dict):
        for key in ("movie_code", "code", "id", "raw", "name", "filename", "file_path"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                source = str(item.get("source") or item.get("file_path") or f"json[{index}]")
                return RawCodeEntry(source=source, raw_value=value)
    return None


def load_entries_from_json(json_path: Path) -> tuple[list[RawCodeEntry], list[str]]:
    with json_path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    entries: list[RawCodeEntry] = []
    errors: list[str] = []

    if isinstance(data, list):
        for index, item in enumerate(data):
            entry = _extract_raw_value_from_json_item(item, index)
            if entry is None:
                errors.append(f"json[{index}] is not a supported code item.")
                continue
            entries.append(entry)
        return entries, errors

    if isinstance(data, dict):
        iterable = data.get("codes")
        if iterable is None:
            iterable = data.get("items")
        if iterable is None:
            entry = _extract_raw_value_from_json_item(data, 0)
            if entry is None:
                errors.append("JSON object does not contain supported code fields.")
                return entries, errors
            entries.append(entry)
            return entries, errors
        if not isinstance(iterable, list):
            errors.append("JSON 'codes'/'items' must be a list.")
            return entries, errors
        for index, item in enumerate(iterable):
            entry = _extract_raw_value_from_json_item(item, index)
            if entry is None:
                errors.append(f"json[{index}] is not a supported code item.")
                continue
            entries.append(entry)
        return entries, errors

    errors.append("Unsupported JSON root type. Expected object or array.")
    return entries, errors


def load_entries_from_input_path(input_path: Path) -> tuple[list[RawCodeEntry], list[str]]:
    files, failures = collect_video_files(input_path)
    entries = [
        RawCodeEntry(source=str(file_path), raw_value=file_path.stem) for file_path in files
    ]
    errors = [failure.message for failure in failures]
    return entries, errors


def _candidate_stem(raw_value: str) -> str:
    raw = raw_value.strip()
    # Accept full path/file-name style values from JSON by extracting the stem.
    if "\\" in raw or "/" in raw:
        return Path(raw).stem
    if "." in raw:
        return Path(raw).stem
    return raw


def extract_codes_payload(
    entries: list[RawCodeEntry],
    input_kind: str,
    input_value: str,
    parse_errors: list[str] | None = None,
) -> dict[str, Any]:
    parse_errors = parse_errors or []
    normalized_items: list[dict[str, str]] = []
    seen_codes: set[str] = set()
    unique_codes: list[str] = []
    invalid_items: list[dict[str, str]] = []

    for entry in entries:
        normalized = extract_standard_movie_code(_candidate_stem(entry.raw_value))
        if not normalized:
            invalid_items.append(
                {
                    "source": entry.source,
                    "raw_value": entry.raw_value,
                    "reason": "NO_STANDARD_CODE",
                }
            )
            continue
        normalized_items.append(
            {
                "source": entry.source,
                "raw_value": entry.raw_value,
                "movie_code": normalized,
            }
        )
        if normalized not in seen_codes:
            seen_codes.add(normalized)
            unique_codes.append(normalized)

    unique_codes.sort()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": {"kind": input_kind, "value": input_value},
        "summary": {
            "total_entries": len(entries),
            "valid_entries": len(normalized_items),
            "invalid_entries": len(invalid_items),
            "unique_codes": len(unique_codes),
            "input_errors": len(parse_errors),
        },
        "codes": unique_codes,
        "items": normalized_items,
        "invalid_items": invalid_items,
        "input_errors": parse_errors,
    }


def write_codes_json(output_path: Path, payload: dict[str, Any]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path

