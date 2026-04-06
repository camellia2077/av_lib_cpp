from __future__ import annotations

import argparse
from pathlib import Path

from .service import (
    extract_codes_payload,
    load_entries_from_input_path,
    load_entries_from_json,
    write_codes_json,
)

DEFAULT_OUTPUT_PATH = Path("out/av_tools/extract_codes/codes.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract normalized movie codes only (no API calls) and export as JSON."
        )
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--input",
        help="Input path: directory (recursive scan) or single video file",
    )
    source_group.add_argument(
        "--codes-json",
        help="Input JSON path containing code-like values",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Output JSON path (default: {DEFAULT_OUTPUT_PATH})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output).expanduser().resolve()

    if args.input:
        input_path = Path(args.input).expanduser().resolve()
        if not input_path.exists():
            raise SystemExit(f"Invalid path: {input_path}")
        entries, errors = load_entries_from_input_path(input_path)
        payload = extract_codes_payload(
            entries=entries,
            input_kind="path",
            input_value=str(input_path),
            parse_errors=errors,
        )
    else:
        json_path = Path(args.codes_json).expanduser().resolve()
        if not json_path.exists() or not json_path.is_file():
            raise SystemExit(f"Invalid JSON path: {json_path}")
        entries, errors = load_entries_from_json(json_path)
        payload = extract_codes_payload(
            entries=entries,
            input_kind="json",
            input_value=str(json_path),
            parse_errors=errors,
        )

    written = write_codes_json(output_path, payload)
    summary = payload["summary"]
    print(
        "[SUMMARY] "
        f"total_entries={summary['total_entries']}, "
        f"valid_entries={summary['valid_entries']}, "
        f"invalid_entries={summary['invalid_entries']}, "
        f"unique_codes={summary['unique_codes']}, "
        f"input_errors={summary['input_errors']}"
    )
    print(f"[OUTPUT] codes_json={written}")

