import json
from pathlib import Path

from apps.av_tools.extract_codes import service


def test_load_entries_from_json_list_and_extract_payload() -> None:
    entries = [
        service.RawCodeEntry(source="json[0]", raw_value="bokd250"),
        service.RawCodeEntry(source="json[1]", raw_value="IPSD-048-A"),
    ]
    payload = service.extract_codes_payload(entries, "json", "inline")

    assert payload["summary"]["total_entries"] == 2
    assert payload["summary"]["unique_codes"] == 2
    assert payload["codes"] == ["BOKD-250", "IPSD-048"]


def test_load_entries_from_json_file(tmp_path: Path) -> None:
    json_path = tmp_path / "codes.json"
    json_path.write_text(
        json.dumps({"codes": ["abc123", {"movie_code": "IPTD-908"}]}, ensure_ascii=False),
        encoding="utf-8",
    )

    entries, errors = service.load_entries_from_json(json_path)

    assert errors == []
    assert len(entries) == 2
    payload = service.extract_codes_payload(entries, "json", str(json_path))
    assert payload["codes"] == ["ABC-123", "IPTD-908"]


def test_load_entries_from_directory_path(tmp_path: Path) -> None:
    (tmp_path / "bokd250.mp4").write_text("x", encoding="utf-8")
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")

    entries, errors = service.load_entries_from_input_path(tmp_path)

    assert errors == []
    assert len(entries) == 1
    payload = service.extract_codes_payload(entries, "path", str(tmp_path))
    assert payload["codes"] == ["BOKD-250"]

