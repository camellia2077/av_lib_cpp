from pathlib import Path

import pytest

from apps.av_tools.move_by_actor.app import cli
from apps.av_tools.move_by_actor.app.config import RuntimeConfigFile


def test_main_start_api_only_does_not_require_input(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["move-by-actor", "--start-api-only"],
    )
    monkeypatch.setattr(cli, "ensure_api_ready", lambda _opts: None)
    monkeypatch.setattr(
        cli,
        "load_runtime_config",
        lambda path, defaults: RuntimeConfigFile(api=defaults.api),
    )

    called = {"move": False}

    def _move_never_called(*_args, **_kwargs):
        called["move"] = True
        return 0, 0, False

    monkeypatch.setattr(cli, "move_videos_by_actor", _move_never_called)

    cli.main()

    assert called["move"] is False


def test_main_returns_130_when_service_reports_interrupted(
    monkeypatch, tmp_path: Path
) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    runtime_toml = tmp_path / "runtime.toml"
    runtime_toml.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "move-by-actor",
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
    monkeypatch.setattr(cli, "move_videos_by_actor", lambda *_args, **_kwargs: (1, 1, True))

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 130


def test_default_runtime_config_path_is_under_apps_av_tools() -> None:
    path = cli.default_runtime_config_path()
    normalized = str(path).replace("\\", "/").lower()
    assert normalized.endswith("/apps/av_tools/move_by_actor/runtime.toml")

