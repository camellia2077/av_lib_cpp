from pathlib import Path

import pytest

from apps.av_tools.providers.browser_fallback_provider import BrowserFallbackProvider

pytest.importorskip("bs4")


def _read_fixture(name: str) -> str:
    path = Path(__file__).resolve().parent / "fixtures" / name
    return path.read_text(encoding="utf-8")


def test_browser_provider_parse_javdb_search_candidates() -> None:
    provider = BrowserFallbackProvider(
        javdb_base_url="https://javdb8.com/",
        r18_base_url="https://www.r18.com/",
        headless=True,
        nav_timeout_sec=15,
    )

    candidates = provider._parse_javdb_search_candidates(_read_fixture("javdb_search.html"))

    assert len(candidates) >= 1
    assert candidates[0].code == "IPSD-048"
    assert candidates[0].url.endswith("/v/abc01")


def test_browser_provider_parse_javdb_detail() -> None:
    provider = BrowserFallbackProvider(
        javdb_base_url="https://javdb8.com/",
        r18_base_url="https://www.r18.com/",
        headless=True,
        nav_timeout_sec=15,
    )

    detail = provider._parse_javdb_detail(_read_fixture("javdb_detail.html"))

    assert detail is not None
    assert detail.code == "IPSD-048"
    assert detail.studio == "IdeaPocket"
    assert detail.series == "Sample Series"
    assert detail.tags == ["Tag1", "Tag2"]
    assert detail.actors == ["Actor A", "Actor B"]


def test_browser_provider_parse_r18_search_candidates() -> None:
    provider = BrowserFallbackProvider(
        javdb_base_url="https://javdb8.com/",
        r18_base_url="https://www.r18.com/",
        headless=True,
        nav_timeout_sec=15,
    )

    candidates = provider._parse_r18_search_candidates(_read_fixture("r18_search.html"))

    assert len(candidates) >= 1
    assert candidates[0].code == "IPTD-908"


def test_browser_provider_parse_r18_detail() -> None:
    provider = BrowserFallbackProvider(
        javdb_base_url="https://javdb8.com/",
        r18_base_url="https://www.r18.com/",
        headless=True,
        nav_timeout_sec=15,
    )

    detail = provider._parse_r18_detail(
        _read_fixture("r18_detail.html"),
        fallback_code="IPTD-908",
    )

    assert detail is not None
    assert detail.code == "IPTD-908"
    assert detail.tags == ["R18Tag1", "R18Tag2"]
    assert detail.actors == ["Actor R18"]
