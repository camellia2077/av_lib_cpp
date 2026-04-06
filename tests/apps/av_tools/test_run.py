import pytest

from apps.av_tools import run


def test_main_passes_remaining_args_to_dispatch(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_dispatch(command: str, forwarded_args: list[str]) -> None:
        captured["command"] = command
        captured["args"] = forwarded_args

    monkeypatch.setattr(run, "_dispatch", fake_dispatch)

    run.main(["index-formatter", "--", "E:\\av\\sample", "--apply"])

    assert captured["command"] == "index-formatter"
    assert captured["args"] == ["E:\\av\\sample", "--apply"]


def test_main_rejects_unknown_subcommand() -> None:
    with pytest.raises(SystemExit) as exc:
        run.main(["unknown"])
    assert exc.value.code == 2


def test_main_accepts_fetch_metadata_subcommand(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_dispatch(command: str, forwarded_args: list[str]) -> None:
        captured["command"] = command
        captured["args"] = forwarded_args

    monkeypatch.setattr(run, "_dispatch", fake_dispatch)

    run.main(["fetch-metadata", "--", "--input", "E:\\av\\sample"])

    assert captured["command"] == "fetch-metadata"
    assert captured["args"] == ["--input", "E:\\av\\sample"]


def test_main_accepts_extract_codes_subcommand(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_dispatch(command: str, forwarded_args: list[str]) -> None:
        captured["command"] = command
        captured["args"] = forwarded_args

    monkeypatch.setattr(run, "_dispatch", fake_dispatch)

    run.main(["extract-codes", "--", "--input", "E:\\av\\sample"])

    assert captured["command"] == "extract-codes"
    assert captured["args"] == ["--input", "E:\\av\\sample"]


def test_main_prints_version(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        run.main(["--version"])

    assert exc.value.code == 0
    output = capsys.readouterr().out.strip()
    assert output.endswith("0.1.0")
