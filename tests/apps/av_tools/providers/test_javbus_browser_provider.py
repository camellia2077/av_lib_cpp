from pathlib import Path

import pytest

from apps.av_tools.providers.javbus_browser_provider import JavbusBrowserProvider

pytest.importorskip("bs4")


def _read_fixture(name: str) -> str:
    path = Path(__file__).resolve().parent / "fixtures" / name
    return path.read_text(encoding="utf-8")


def test_javbus_browser_parse_search_candidates() -> None:
    provider = JavbusBrowserProvider(
        base_url="https://www.javbus.com/",
        headless=True,
        nav_timeout_sec=15,
    )

    candidates = provider._parse_search_candidates(_read_fixture("javbus_search.html"))

    assert len(candidates) >= 1
    assert candidates[0].code == "MOON-011"
    assert candidates[0].url == "https://www.javbus.com/MOON-011"


def test_javbus_browser_normalize_supports_uncensored_date_codes() -> None:
    assert JavbusBrowserProvider._normalize_code("031315-827") == "031315-827"
    assert JavbusBrowserProvider._normalize_code("031315-827-carib") == "031315-827"
    assert JavbusBrowserProvider._normalize_code("091416_382-1pondo") == "091416_382"


def test_javbus_browser_parse_detail_fields() -> None:
    provider = JavbusBrowserProvider(
        base_url="https://www.javbus.com/",
        headless=True,
        nav_timeout_sec=15,
    )

    detail = provider._parse_detail(
        _read_fixture("javbus_detail.html"),
        url="https://www.javbus.com/MOON-011",
    )

    assert detail is not None
    assert detail.code == "MOON-011"
    assert detail.date == "2024-01-01"
    assert detail.studio == "MOODYZ"
    assert detail.series == "Sample Series"
    assert detail.actors == ["天馬ゆい"]
    assert detail.tags == ["中出", "美少女"]


def test_javbus_browser_builds_uncensored_search_urls_for_date_code() -> None:
    provider = JavbusBrowserProvider(
        base_url="https://www.javbus.com/",
        headless=True,
        nav_timeout_sec=15,
    )

    urls = provider._build_search_urls("091416_382")

    assert urls[0].startswith("https://www.javbus.com/uncensored/search/")
    assert any("/uncensored/search/091416-382" in item for item in urls)
    assert any("/search/091416_382" in item for item in urls)


def test_javbus_browser_fetch_with_context_uses_best_candidate(monkeypatch) -> None:
    provider = JavbusBrowserProvider(
        base_url="https://www.javbus.com/",
        headless=True,
        nav_timeout_sec=15,
    )
    search_html = _read_fixture("javbus_search.html")
    detail_html = _read_fixture("javbus_detail.html")

    def fake_browser_get(_context, url: str):
        if "/search/" in url:
            return 200, search_html, url, "MOON-011 - 搜尋 - 影片 - JavBus"
        return 200, detail_html, url, "MOON-011 - JavBus"

    monkeypatch.setattr(provider, "_browser_get", fake_browser_get)

    result = provider._fetch_with_context("MOON-011", context=object())

    assert result.status == "success"
    assert result.movie is not None
    assert result.movie.title == "顔射ザーメン全部飲む。 天馬ゆい"


def test_javbus_browser_fetch_with_context_marks_cloudflare_as_error(monkeypatch) -> None:
    provider = JavbusBrowserProvider(
        base_url="https://www.javbus.com/",
        headless=True,
        nav_timeout_sec=15,
    )
    cloudflare_html = _read_fixture("javbus_cloudflare.html")

    def fake_browser_get(_context, url: str):
        return 200, cloudflare_html, url, "Attention Required! | Cloudflare"

    monkeypatch.setattr(provider, "_browser_get", fake_browser_get)

    result = provider._fetch_with_context("MOON-011", context=object())

    assert result.status == "error"
    assert "blocked=cloudflare" in result.message
