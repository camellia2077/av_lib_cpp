from pathlib import Path

import pytest

from apps.av_tools.fetch_metadata import cli
from apps.av_tools.fetch_metadata.models import FetchSummary
from apps.av_tools.move_by_actor.app.config import RuntimeConfigFile


def test_fetch_metadata_cli_start_api_only_does_not_require_input(monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["fetch-metadata", "--start-api-only"])
    monkeypatch.setattr(cli, "ensure_api_ready", lambda _opts: None)
    monkeypatch.setattr(
        cli,
        "load_runtime_config",
        lambda path, defaults: RuntimeConfigFile(api=defaults.api),
    )

    called = {"fetch": False}

    def fake_fetch(*_args, **_kwargs):
        called["fetch"] = True
        return [], [], FetchSummary(0, 0, 0, 0, 0)

    monkeypatch.setattr(cli, "fetch_metadata", fake_fetch)
    monkeypatch.setattr(cli, "write_json_reports", lambda *_args, **_kwargs: {})

    cli.main()

    assert called["fetch"] is False


def test_fetch_metadata_cli_accepts_directory_input(monkeypatch, tmp_path: Path) -> None:
    input_dir = tmp_path / "videos"
    input_dir.mkdir()
    runtime_toml = tmp_path / "runtime.toml"
    runtime_toml.write_text("", encoding="utf-8")
    output_dir = tmp_path / "out"

    monkeypatch.setattr(
        "sys.argv",
        [
            "fetch-metadata",
            "--input",
            str(input_dir),
            "--output-dir",
            str(output_dir),
            "--runtime-config",
            str(runtime_toml),
            "--request-interval",
            "0",
        ],
    )
    monkeypatch.setattr(cli, "ensure_api_ready", lambda _opts: None)
    monkeypatch.setattr(
        cli,
        "load_runtime_config",
        lambda path, defaults: RuntimeConfigFile(api=defaults.api),
    )

    captured: dict[str, object] = {}

    def fake_fetch(input_path: Path, cfg, **kwargs):
        del cfg
        captured["input_path"] = input_path
        captured["request_interval_sec"] = kwargs.get("request_interval_sec")
        return [], [], FetchSummary(0, 0, 0, 0, 0)

    monkeypatch.setattr(cli, "fetch_metadata", fake_fetch)
    monkeypatch.setattr(
        cli,
        "write_json_reports",
        lambda output_dir, input_path, records, failures, summary: {
            "result_json": output_dir / "result.json",
            "failed_json": output_dir / "failed.json",
        },
    )

    cli.main()

    assert captured["input_path"] == input_dir.resolve()
    assert captured["request_interval_sec"] == 0.0


def test_fetch_metadata_cli_invalid_path_exits(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["fetch-metadata", "--input", "Z:\\this_path_should_not_exist_123"],
    )

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert "Invalid path" in str(exc.value)


def test_fetch_metadata_cli_returns_130_on_interrupt(
    monkeypatch, tmp_path: Path
) -> None:
    input_dir = tmp_path / "videos"
    input_dir.mkdir()
    runtime_toml = tmp_path / "runtime.toml"
    runtime_toml.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "fetch-metadata",
            "--input",
            str(input_dir),
            "--runtime-config",
            str(runtime_toml),
        ],
    )
    monkeypatch.setattr(cli, "ensure_api_ready", lambda _opts: None)
    monkeypatch.setattr(
        cli,
        "load_runtime_config",
        lambda path, defaults: RuntimeConfigFile(api=defaults.api),
    )
    monkeypatch.setattr(
        cli,
        "fetch_metadata",
        lambda input_path, cfg, **kwargs: (_ for _ in ()).throw(KeyboardInterrupt()),
    )

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 130
