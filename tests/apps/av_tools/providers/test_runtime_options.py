from pathlib import Path

from apps.av_tools.providers.runtime_options import load_providers_runtime_options


def test_load_providers_runtime_options_reads_provider_settings(tmp_path: Path) -> None:
    runtime_toml = tmp_path / "runtime.toml"
    runtime_toml.write_text(
        """
[providers]
enabled = ["javbus_api", "javdb"]

[providers.network]
timeout_sec = 33
request_interval_sec = 1.5

[providers.javdb]
enabled = true
base_url = "https://javdb.example/"

[providers.r18]
enabled = false
base_url = "https://r18.example/"

[providers.javbus_browser]
enabled = true
base_url = "https://www.javbus.com/"
headless = false
nav_timeout_sec = 9

[providers.browser_fallback]
mode = "on_error"
headless = false
nav_timeout_sec = 12
""".strip(),
        encoding="utf-8",
    )

    options = load_providers_runtime_options(runtime_toml)

    assert options.enabled == ["javbus_api", "javdb"]
    assert options.network.timeout_sec == 33
    assert options.network.request_interval_sec == 1.5
    assert options.javdb.base_url == "https://javdb.example/"
    assert options.r18.enabled is False
    assert options.javbus_browser.enabled is True
    assert options.javbus_browser.base_url == "https://www.javbus.com/"
    assert options.javbus_browser.headless is False
    assert options.javbus_browser.nav_timeout_sec == 9.0
    assert options.browser_fallback.mode == "on_error"
    assert options.browser_fallback.headless is False
    assert options.browser_fallback.nav_timeout_sec == 12.0


def test_load_providers_runtime_options_supports_browser_only_mode(tmp_path: Path) -> None:
    runtime_toml = tmp_path / "runtime.toml"
    runtime_toml.write_text(
        """
[providers.browser_fallback]
mode = "only"
""".strip(),
        encoding="utf-8",
    )

    options = load_providers_runtime_options(runtime_toml)

    assert options.browser_fallback.mode == "only"
