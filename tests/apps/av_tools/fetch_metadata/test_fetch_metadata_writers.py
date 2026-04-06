import json
from pathlib import Path

from apps.av_tools.fetch_metadata.models import FetchSummary, MetadataFailure, MetadataRecord
from apps.av_tools.fetch_metadata.writers import StreamingReportWriter, write_reports


def test_write_reports_creates_json_and_csv_outputs(tmp_path: Path) -> None:
    output_dir = tmp_path / "reports"
    input_path = tmp_path / "input"
    input_path.mkdir()

    records = [
        MetadataRecord(
            file_path=str(input_path / "ABC-123.mp4"),
            movie_code="ABC-123",
            title="Movie Title",
            actors=["Actor A", "Actor B"],
            tags=["NTR", "Drama"],
            cover_url="https://example.com/c.jpg",
        )
    ]
    failures = [
        MetadataFailure(
            file_path=str(input_path / "bad.mp4"),
            reason="NO_CODE",
            message="Cannot parse code",
        )
    ]
    summary = FetchSummary(
        scanned_files=2,
        success_count=1,
        failed_count=1,
        api_queries=1,
        api_cache_hits=0,
    )

    outputs = write_reports(output_dir, input_path, records, failures, summary)

    for path in outputs.values():
        assert path.exists()

    result_payload = json.loads(outputs["result_json"].read_text(encoding="utf-8"))
    failed_payload = json.loads(outputs["failed_json"].read_text(encoding="utf-8"))
    assert result_payload["summary"]["success_count"] == 1
    assert failed_payload["summary"]["failed_count"] == 1
    assert result_payload["items"][0]["cover_url"] == "https://example.com/c.jpg"
    assert result_payload["items"][0]["tags"] == ["NTR", "Drama"]

    result_csv = outputs["result_csv"].read_text(encoding="utf-8")
    failed_csv = outputs["failed_csv"].read_text(encoding="utf-8")
    assert "actors,movie_code,title,tags,cover_url" in result_csv
    assert "ABC-123" in result_csv
    assert "NTR, Drama" in result_csv
    assert "reason,movie_code,message" in failed_csv
    assert "NO_CODE" in failed_csv


def test_streaming_report_writer_appends_rows(tmp_path: Path) -> None:
    writer = StreamingReportWriter(tmp_path / "stream")
    writer.append_success(
        MetadataRecord(
            file_path="D:/videos/ABC-123.mp4",
            movie_code="ABC-123",
            title="Title",
            actors=["Actor"],
            tags=["Tag"],
            cover_url="https://example.com/c.jpg",
        )
    )
    writer.append_failure(
        MetadataFailure(
            file_path="D:/videos/BAD.mp4",
            reason="NO_CODE",
            message="Cannot parse code",
        )
    )
    writer.close()

    result_csv = (tmp_path / "stream" / "result.csv").read_text(encoding="utf-8")
    failed_csv = (tmp_path / "stream" / "failed.csv").read_text(encoding="utf-8")
    assert "ABC-123" in result_csv
    assert "NO_CODE" in failed_csv
