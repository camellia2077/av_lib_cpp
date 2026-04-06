from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import FetchSummary, MetadataFailure, MetadataRecord


def _summary_payload(summary: FetchSummary) -> dict[str, int]:
    return {
        "scanned_files": summary.scanned_files,
        "success_count": summary.success_count,
        "failed_count": summary.failed_count,
        "api_queries": summary.api_queries,
        "api_cache_hits": summary.api_cache_hits,
    }


def _record_payload(record: MetadataRecord) -> dict[str, Any]:
    return {
        "file_path": record.file_path,
        "movie_code": record.movie_code,
        "title": record.title,
        "actors": record.actors,
        "tags": record.tags,
        "cover_url": record.cover_url,
    }


def _failure_payload(failure: MetadataFailure) -> dict[str, str]:
    return {
        "file_path": failure.file_path,
        "movie_code": failure.movie_code,
        "reason": failure.reason,
        "message": failure.message,
    }


class _StreamingCsvFile:
    def __init__(self, path: Path, headers: list[str]) -> None:
        self.path = path
        self._closed = False
        self._fp = path.open("w", encoding="utf-8", newline="")
        self._writer = csv.writer(self._fp)
        self._writer.writerow(headers)
        self._fp.flush()

    def append(self, row: list[str]) -> None:
        if self._closed:
            return
        self._writer.writerow(row)
        self._fp.flush()

    def close(self) -> None:
        if self._closed:
            return
        self._fp.flush()
        self._fp.close()
        self._closed = True


class StreamingReportWriter:
    def __init__(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        self.result_csv_path = output_dir / "result.csv"
        self.failed_csv_path = output_dir / "failed.csv"
        self._result_csv = _StreamingCsvFile(
            self.result_csv_path,
            ["actors", "movie_code", "title", "tags", "cover_url"],
        )
        self._failed_csv = _StreamingCsvFile(
            self.failed_csv_path,
            ["reason", "movie_code", "message"],
        )

    def append_success(self, record: MetadataRecord) -> None:
        self._result_csv.append(
            [
                ", ".join(record.actors),
                record.movie_code,
                record.title,
                ", ".join(record.tags),
                record.cover_url,
            ]
        )

    def append_failure(self, failure: MetadataFailure) -> None:
        self._failed_csv.append(
            [failure.reason, failure.movie_code, failure.message]
        )

    def close(self) -> None:
        self._result_csv.close()
        self._failed_csv.close()

    def output_paths(self) -> dict[str, Path]:
        return {
            "result_csv": self.result_csv_path,
            "failed_csv": self.failed_csv_path,
        }


def write_json_reports(
    output_dir: Path,
    input_path: Path,
    records: list[MetadataRecord],
    failures: list[MetadataFailure],
    summary: FetchSummary,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()

    result_json_path = output_dir / "result.json"
    failed_json_path = output_dir / "failed.json"

    result_payload = {
        "generated_at": generated_at,
        "input_path": str(input_path),
        "summary": _summary_payload(summary),
        "items": [_record_payload(record) for record in records],
    }
    failed_payload = {
        "generated_at": generated_at,
        "input_path": str(input_path),
        "summary": _summary_payload(summary),
        "items": [_failure_payload(failure) for failure in failures],
    }

    result_json_path.write_text(
        json.dumps(result_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    failed_json_path.write_text(
        json.dumps(failed_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"result_json": result_json_path, "failed_json": failed_json_path}


def write_reports(
    output_dir: Path,
    input_path: Path,
    records: list[MetadataRecord],
    failures: list[MetadataFailure],
    summary: FetchSummary,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_paths = write_json_reports(
        output_dir=output_dir,
        input_path=input_path,
        records=records,
        failures=failures,
        summary=summary,
    )
    result_csv_path = output_dir / "result.csv"
    failed_csv_path = output_dir / "failed.csv"

    with result_csv_path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["actors", "movie_code", "title", "tags", "cover_url"])
        for record in records:
            writer.writerow(
                [
                    ", ".join(record.actors),
                    record.movie_code,
                    record.title,
                    ", ".join(record.tags),
                    record.cover_url,
                ]
            )

    with failed_csv_path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["reason", "movie_code", "message"])
        for failure in failures:
            writer.writerow(
                [
                    failure.reason,
                    failure.movie_code,
                    failure.message,
                ]
            )

    return {
        "result_json": json_paths["result_json"],
        "failed_json": json_paths["failed_json"],
        "result_csv": result_csv_path,
        "failed_csv": failed_csv_path,
    }
