from pathlib import Path

from apps.av_tools.move_by_actor.app.config import Config
from apps.av_tools.providers.javdb_provider import JavdbProvider


def _read_fixture(name: str) -> str:
    path = (
        Path(__file__).resolve().parent
        / "fixtures"
        / name
    )
    return path.read_text(encoding="utf-8")


def test_javdb_parse_search_candidates() -> None:
    provider = JavdbProvider(base_url="https://javdb8.com/", timeout_sec=20, use_env_proxy=False)
    candidates = provider._parse_search_candidates(_read_fixture("javdb_search.html"))

    assert len(candidates) >= 1
    assert candidates[0].code == "IPSD-048"
    assert candidates[0].url.endswith("/v/abc01")


def test_javdb_parse_detail_fields() -> None:
    provider = JavdbProvider(base_url="https://javdb8.com/", timeout_sec=20, use_env_proxy=False)
    detail = provider._parse_detail(_read_fixture("javdb_detail.html"), url="https://javdb8.com/v/abc01")

    assert detail is not None
    assert detail.code == "IPSD-048"
    assert detail.studio == "IdeaPocket"
    assert detail.series == "Sample Series"
    assert detail.tags == ["Tag1", "Tag2"]
    assert detail.actors == ["Actor A", "Actor B"]


def test_javdb_fetch_movie_info_via_fixture_http(monkeypatch) -> None:
    provider = JavdbProvider(base_url="https://javdb8.com/", timeout_sec=20, use_env_proxy=False)
    search_html = _read_fixture("javdb_search.html")
    detail_html = _read_fixture("javdb_detail.html")

    def fake_http_get(url: str):
        if "search?" in url:
            return 200, search_html
        return 200, detail_html

    monkeypatch.setattr(provider, "_http_get", fake_http_get)
    result = provider.fetch_movie_info("IPSD-048", Config())

    assert result.status == "success"
    assert result.movie is not None
    assert result.movie.title == "Sample Movie Title"

