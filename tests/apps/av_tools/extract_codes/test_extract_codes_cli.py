import json
from pathlib import Path

from apps.av_tools.extract_codes import cli


def test_extract_codes_cli_from_input_path(monkeypatch, tmp_path: Path) -> None:
    input_dir = tmp_path / "videos"
    input_dir.mkdir()
    (input_dir / "BOKD250.mp4").write_text("x", encoding="utf-8")
    output_path = tmp_path / "out" / "codes.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "extract-codes",
            "--input",
            str(input_dir),
            "--output",
            str(output_path),
        ],
    )
    cli.main()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["codes"] == ["BOKD-250"]


def test_extract_codes_cli_from_codes_json(monkeypatch, tmp_path: Path) -> None:
    source_json = tmp_path / "source.json"
    source_json.write_text(
        json.dumps({"codes": ["IPSD-048-A", "abc123"]}, ensure_ascii=False),
        encoding="utf-8",
    )
    output_path = tmp_path / "out" / "codes.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "extract-codes",
            "--codes-json",
            str(source_json),
            "--output",
            str(output_path),
        ],
    )
    cli.main()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["codes"] == ["ABC-123", "IPSD-048"]

