from pathlib import Path

import pytest

from apps.av_tools.fetch_metadata import cli
from apps.av_tools.fetch_metadata.models import FetchSummary
from apps.av_tools.move_by_actor.app.config import RuntimeConfigFile
from apps.av_tools.providers.runtime_options import (
    BrowserFallbackOptions,
    JavbusBrowserOptions,
    ProvidersRuntimeOptions,
)


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


def test_fetch_metadata_cli_accepts_codes_json(monkeypatch, tmp_path: Path) -> None:
    codes_json = tmp_path / "codes.json"
    codes_json.write_text('{"codes": ["ABC-123"]}', encoding="utf-8")
    runtime_toml = tmp_path / "runtime.toml"
    runtime_toml.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "fetch-metadata",
            "--codes-json",
            str(codes_json),
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

    def fake_fetch(codes_json_path: Path, cfg, **kwargs):
        del cfg
        captured["codes_json_path"] = codes_json_path
        captured["request_interval_sec"] = kwargs.get("request_interval_sec")
        return [], [], FetchSummary(0, 0, 0, 0, 0)

    monkeypatch.setattr(cli, "fetch_metadata_from_codes_json", fake_fetch)
    monkeypatch.setattr(
        cli,
        "write_json_reports",
        lambda output_dir, input_path, records, failures, summary: {
            "result_json": output_dir / "result.json",
            "failed_json": output_dir / "failed.json",
        },
    )

    cli.main()

    assert captured["codes_json_path"] == codes_json.resolve()
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


def test_fetch_metadata_cli_download_mode_overrides_runtime_toml(
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
            "--download-mode",
            "http",
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
    monkeypatch.setattr(
        cli,
        "load_providers_runtime_options",
        lambda _path: ProvidersRuntimeOptions(
            browser_fallback=BrowserFallbackOptions(mode="on_error")
        ),
    )

    captured: dict[str, object] = {}

    def fake_build_provider_manager(provider_runtime, use_env_proxy):
        captured["mode"] = provider_runtime.browser_fallback.mode
        captured["enabled"] = provider_runtime.enabled
        captured["use_env_proxy"] = use_env_proxy
        return object()

    monkeypatch.setattr(cli, "build_provider_manager_from_runtime", fake_build_provider_manager)
    monkeypatch.setattr(
        cli,
        "fetch_metadata",
        lambda input_path, cfg, **kwargs: ([], [], FetchSummary(0, 0, 0, 0, 0)),
    )
    monkeypatch.setattr(
        cli,
        "write_json_reports",
        lambda output_dir, input_path, records, failures, summary: {
            "result_json": output_dir / "result.json",
            "failed_json": output_dir / "failed.json",
        },
    )

    cli.main()

    assert captured["mode"] == "off"
    assert captured["enabled"] == ["javdb", "javbus_api", "r18"]


def test_fetch_metadata_cli_download_mode_api_only_forces_javbus_api(
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
            "--download-mode",
            "api-only",
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
    monkeypatch.setattr(
        cli,
        "load_providers_runtime_options",
        lambda _path: ProvidersRuntimeOptions(
            enabled=["javdb", "javbus_api", "r18"],
            browser_fallback=BrowserFallbackOptions(mode="always"),
        ),
    )

    captured: dict[str, object] = {}

    def fake_build_provider_manager(provider_runtime, use_env_proxy):
        captured["mode"] = provider_runtime.browser_fallback.mode
        captured["enabled"] = provider_runtime.enabled
        captured["use_env_proxy"] = use_env_proxy
        return object()

    monkeypatch.setattr(cli, "build_provider_manager_from_runtime", fake_build_provider_manager)
    monkeypatch.setattr(
        cli,
        "fetch_metadata",
        lambda input_path, cfg, **kwargs: ([], [], FetchSummary(0, 0, 0, 0, 0)),
    )
    monkeypatch.setattr(
        cli,
        "write_json_reports",
        lambda output_dir, input_path, records, failures, summary: {
            "result_json": output_dir / "result.json",
            "failed_json": output_dir / "failed.json",
        },
    )

    cli.main()

    assert captured["mode"] == "off"
    assert captured["enabled"] == ["javbus_api"]


def test_fetch_metadata_cli_providers_overrides_runtime_order(
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
            "--providers",
            "javdb,r18",
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
    monkeypatch.setattr(
        cli,
        "load_providers_runtime_options",
        lambda _path: ProvidersRuntimeOptions(enabled=["javbus_api", "javdb", "r18"]),
    )

    captured: dict[str, object] = {}

    def fake_build_provider_manager(provider_runtime, use_env_proxy):
        captured["enabled"] = provider_runtime.enabled
        captured["use_env_proxy"] = use_env_proxy
        return object()

    monkeypatch.setattr(cli, "build_provider_manager_from_runtime", fake_build_provider_manager)
    monkeypatch.setattr(
        cli,
        "fetch_metadata",
        lambda input_path, cfg, **kwargs: ([], [], FetchSummary(0, 0, 0, 0, 0)),
    )
    monkeypatch.setattr(
        cli,
        "write_json_reports",
        lambda output_dir, input_path, records, failures, summary: {
            "result_json": output_dir / "result.json",
            "failed_json": output_dir / "failed.json",
        },
    )

    cli.main()

    assert captured["enabled"] == ["javdb", "r18"]


def test_fetch_metadata_cli_providers_accepts_javbus_browser(
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
            "--providers",
            "javbus_browser,javdb",
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
    monkeypatch.setattr(
        cli,
        "load_providers_runtime_options",
        lambda _path: ProvidersRuntimeOptions(),
    )

    captured: dict[str, object] = {}

    def fake_build_provider_manager(provider_runtime, use_env_proxy):
        captured["enabled"] = provider_runtime.enabled
        captured["javbus_browser_enabled"] = provider_runtime.javbus_browser.enabled
        captured["use_env_proxy"] = use_env_proxy
        return object()

    monkeypatch.setattr(cli, "build_provider_manager_from_runtime", fake_build_provider_manager)
    monkeypatch.setattr(
        cli,
        "fetch_metadata",
        lambda input_path, cfg, **kwargs: ([], [], FetchSummary(0, 0, 0, 0, 0)),
    )
    monkeypatch.setattr(
        cli,
        "write_json_reports",
        lambda output_dir, input_path, records, failures, summary: {
            "result_json": output_dir / "result.json",
            "failed_json": output_dir / "failed.json",
        },
    )

    cli.main()

    assert captured["enabled"] == ["javbus_browser", "javdb"]
    assert captured["javbus_browser_enabled"] is True


def test_fetch_metadata_cli_providers_rejects_unsupported_name(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "fetch-metadata",
            "--input",
            "C:\\dummy",
            "--providers",
            "javdb,unknown",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert "Unsupported provider(s)" in str(exc.value)


def test_fetch_metadata_cli_provider_timeout_overrides_runtime(
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
            "--provider-timeout",
            "6",
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
    monkeypatch.setattr(
        cli,
        "load_providers_runtime_options",
        lambda _path: ProvidersRuntimeOptions(),
    )

    captured: dict[str, object] = {}

    def fake_build_provider_manager(provider_runtime, use_env_proxy):
        captured["provider_timeout"] = provider_runtime.network.timeout_sec
        captured["use_env_proxy"] = use_env_proxy
        return object()

    monkeypatch.setattr(cli, "build_provider_manager_from_runtime", fake_build_provider_manager)
    monkeypatch.setattr(
        cli,
        "fetch_metadata",
        lambda input_path, cfg, **kwargs: ([], [], FetchSummary(0, 0, 0, 0, 0)),
    )
    monkeypatch.setattr(
        cli,
        "write_json_reports",
        lambda output_dir, input_path, records, failures, summary: {
            "result_json": output_dir / "result.json",
            "failed_json": output_dir / "failed.json",
        },
    )

    cli.main()

    assert captured["provider_timeout"] == 6


def test_fetch_metadata_cli_download_mode_browser_only(
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
            "--download-mode",
            "browser-only",
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
    monkeypatch.setattr(
        cli,
        "load_providers_runtime_options",
        lambda _path: ProvidersRuntimeOptions(enabled=["javdb", "javbus_api", "r18"]),
    )

    captured: dict[str, object] = {}

    def fake_build_provider_manager(provider_runtime, use_env_proxy):
        captured["mode"] = provider_runtime.browser_fallback.mode
        captured["enabled"] = provider_runtime.enabled
        captured["javbus_browser_enabled"] = provider_runtime.javbus_browser.enabled
        captured["use_env_proxy"] = use_env_proxy
        return object()

    monkeypatch.setattr(cli, "build_provider_manager_from_runtime", fake_build_provider_manager)
    monkeypatch.setattr(
        cli,
        "fetch_metadata",
        lambda input_path, cfg, **kwargs: ([], [], FetchSummary(0, 0, 0, 0, 0)),
    )
    monkeypatch.setattr(
        cli,
        "write_json_reports",
        lambda output_dir, input_path, records, failures, summary: {
            "result_json": output_dir / "result.json",
            "failed_json": output_dir / "failed.json",
        },
    )

    cli.main()

    assert captured["mode"] == "off"
    assert captured["enabled"] == ["javbus_browser"]
    assert captured["javbus_browser_enabled"] is True


def test_fetch_metadata_cli_show_browser_forces_headed(
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
            "--show-browser",
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
    monkeypatch.setattr(
        cli,
        "load_providers_runtime_options",
        lambda _path: ProvidersRuntimeOptions(
            browser_fallback=BrowserFallbackOptions(mode="on_error", headless=True),
            javbus_browser=JavbusBrowserOptions(enabled=True, headless=True),
        ),
    )

    captured: dict[str, object] = {}

    def fake_build_provider_manager(provider_runtime, use_env_proxy):
        captured["fallback_headless"] = provider_runtime.browser_fallback.headless
        captured["javbus_browser_headless"] = provider_runtime.javbus_browser.headless
        captured["use_env_proxy"] = use_env_proxy
        return object()

    monkeypatch.setattr(cli, "build_provider_manager_from_runtime", fake_build_provider_manager)
    monkeypatch.setattr(
        cli,
        "fetch_metadata",
        lambda input_path, cfg, **kwargs: ([], [], FetchSummary(0, 0, 0, 0, 0)),
    )
    monkeypatch.setattr(
        cli,
        "write_json_reports",
        lambda output_dir, input_path, records, failures, summary: {
            "result_json": output_dir / "result.json",
            "failed_json": output_dir / "failed.json",
        },
    )

    cli.main()

    assert captured["fallback_headless"] is False
    assert captured["javbus_browser_headless"] is False
