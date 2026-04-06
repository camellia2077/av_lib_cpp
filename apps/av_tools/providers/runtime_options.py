from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise RuntimeError("Python 3.11+ is required for TOML support.") from exc


@dataclass(frozen=True)
class ProviderNetworkOptions:
    timeout_sec: int = 20
    request_interval_sec: float = 1.0


@dataclass(frozen=True)
class ProviderSourceOptions:
    enabled: bool = True
    base_url: str = ""


@dataclass(frozen=True)
class JavbusBrowserOptions:
    enabled: bool = False
    base_url: str = "https://www.javbus.com/"
    headless: bool = True
    nav_timeout_sec: float = 15.0


BrowserFallbackMode = Literal["off", "on_error", "always", "only"]


@dataclass(frozen=True)
class BrowserFallbackOptions:
    mode: BrowserFallbackMode = "off"
    headless: bool = True
    nav_timeout_sec: float = 15.0


@dataclass(frozen=True)
class ProvidersRuntimeOptions:
    enabled: list[str] = field(
        default_factory=lambda: ["javdb", "javbus_api", "r18"]
    )
    network: ProviderNetworkOptions = field(default_factory=ProviderNetworkOptions)
    javdb: ProviderSourceOptions = field(
        default_factory=lambda: ProviderSourceOptions(
            enabled=True, base_url="https://javdb8.com/"
        )
    )
    javbus_api: ProviderSourceOptions = field(
        default_factory=lambda: ProviderSourceOptions(enabled=True, base_url="")
    )
    r18: ProviderSourceOptions = field(
        default_factory=lambda: ProviderSourceOptions(
            enabled=True, base_url="https://www.r18.com/"
        )
    )
    javbus_browser: JavbusBrowserOptions = field(default_factory=JavbusBrowserOptions)
    browser_fallback: BrowserFallbackOptions = field(
        default_factory=BrowserFallbackOptions
    )


def _as_bool(raw: Any, default: bool) -> bool:
    return raw if isinstance(raw, bool) else default


def _as_str(raw: Any, default: str) -> str:
    return raw.strip() if isinstance(raw, str) and raw.strip() else default


def _as_int(raw: Any, default: int) -> int:
    return int(raw) if isinstance(raw, int) else default


def _as_float(raw: Any, default: float) -> float:
    if isinstance(raw, (int, float)):
        return float(raw)
    return default


def _as_str_list(raw: Any, default: list[str]) -> list[str]:
    if not isinstance(raw, list):
        return default
    values = [str(item).strip() for item in raw if str(item).strip()]
    return values or default


def _read_source(
    section: Any, defaults: ProviderSourceOptions
) -> ProviderSourceOptions:
    if not isinstance(section, dict):
        return defaults
    return ProviderSourceOptions(
        enabled=_as_bool(section.get("enabled"), defaults.enabled),
        base_url=_as_str(section.get("base_url"), defaults.base_url),
    )


def _as_browser_mode(raw: Any, default: BrowserFallbackMode) -> BrowserFallbackMode:
    if not isinstance(raw, str):
        return default
    value = raw.strip().lower()
    if value in {"off", "on_error", "always", "only"}:
        return value  # type: ignore[return-value]
    return default


def _read_browser_fallback(
    section: Any, defaults: BrowserFallbackOptions
) -> BrowserFallbackOptions:
    if not isinstance(section, dict):
        return defaults
    return BrowserFallbackOptions(
        mode=_as_browser_mode(section.get("mode"), defaults.mode),
        headless=_as_bool(section.get("headless"), defaults.headless),
        nav_timeout_sec=max(
            1.0,
            _as_float(section.get("nav_timeout_sec"), defaults.nav_timeout_sec),
        ),
    )


def _read_javbus_browser(
    section: Any, defaults: JavbusBrowserOptions
) -> JavbusBrowserOptions:
    if not isinstance(section, dict):
        return defaults
    return JavbusBrowserOptions(
        enabled=_as_bool(section.get("enabled"), defaults.enabled),
        base_url=_as_str(section.get("base_url"), defaults.base_url),
        headless=_as_bool(section.get("headless"), defaults.headless),
        nav_timeout_sec=max(
            1.0,
            _as_float(section.get("nav_timeout_sec"), defaults.nav_timeout_sec),
        ),
    )


def load_providers_runtime_options(path: Path) -> ProvidersRuntimeOptions:
    defaults = ProvidersRuntimeOptions()
    if not path.exists():
        return defaults

    with path.open("rb") as fp:
        raw = tomllib.load(fp)
    if not isinstance(raw, dict):
        return defaults

    providers = raw.get("providers", {})
    if not isinstance(providers, dict):
        return defaults

    network_raw = providers.get("network", {})
    if not isinstance(network_raw, dict):
        network_raw = {}

    network = ProviderNetworkOptions(
        timeout_sec=max(1, _as_int(network_raw.get("timeout_sec"), defaults.network.timeout_sec)),
        request_interval_sec=max(
            0.0,
            _as_float(
                network_raw.get("request_interval_sec"),
                defaults.network.request_interval_sec,
            ),
        ),
    )
    return ProvidersRuntimeOptions(
        enabled=_as_str_list(providers.get("enabled"), defaults.enabled),
        network=network,
        javdb=_read_source(providers.get("javdb"), defaults.javdb),
        javbus_api=_read_source(providers.get("javbus_api"), defaults.javbus_api),
        r18=_read_source(providers.get("r18"), defaults.r18),
        javbus_browser=_read_javbus_browser(
            providers.get("javbus_browser"),
            defaults.javbus_browser,
        ),
        browser_fallback=_read_browser_fallback(
            providers.get("browser_fallback"),
            defaults.browser_fallback,
        ),
    )
