from pathlib import Path

from apps.av_tools.move_by_actor.app.config import Config
from apps.av_tools.providers.r18_provider import R18Provider


def _read_fixture(name: str) -> str:
    path = (
        Path(__file__).resolve().parent
        / "fixtures"
        / name
    )
    return path.read_text(encoding="utf-8")


def test_r18_parse_search_candidates() -> None:
    provider = R18Provider(base_url="https://www.r18.com/", timeout_sec=20, use_env_proxy=False)
    candidates = provider._parse_search_candidates(_read_fixture("r18_search.html"))

    assert len(candidates) >= 1
    assert candidates[0].code == "IPTD-908"


def test_r18_parse_detail_fields() -> None:
    provider = R18Provider(base_url="https://www.r18.com/", timeout_sec=20, use_env_proxy=False)
    detail = provider._parse_detail(_read_fixture("r18_detail.html"), fallback_code="IPTD-908")

    assert detail is not None
    assert detail.code == "IPTD-908"
    assert detail.tags == ["R18Tag1", "R18Tag2"]
    assert detail.actors == ["Actor R18"]


def test_r18_fetch_movie_info_via_fixture_http(monkeypatch) -> None:
    provider = R18Provider(base_url="https://www.r18.com/", timeout_sec=20, use_env_proxy=False)
    search_html = _read_fixture("r18_search.html")
    detail_html = _read_fixture("r18_detail.html")

    def fake_http_get(url: str):
        if "searchword=" in url:
            return 200, search_html
        return 200, detail_html

    monkeypatch.setattr(provider, "_http_get", fake_http_get)
    result = provider.fetch_movie_info("IPTD-908", Config())

    assert result.status == "success"
    assert result.movie is not None
    assert result.movie.title == "Sample Movie Title"

