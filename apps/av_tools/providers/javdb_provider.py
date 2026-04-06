from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote, urljoin

import requests

from ..move_by_actor.app.config import Config
from ..move_by_actor.app.models import MovieInfo
from .base import ProviderFetchResult
from .utils import Candidate, expand_query_keys, select_best_candidate

JAVDB_SEARCH_ITEM_PATTERN = re.compile(
    r'<a[^>]+href="(?P<href>/v/[^"]+)"[^>]*>.*?'
    r'<div[^>]+class="uid[^"]*"[^>]*>(?P<code>[^<]+)</div>.*?'
    r'<div[^>]+class="video-title[^"]*"[^>]*>(?P<title>.*?)</div>.*?'
    r'(?:<img[^>]+(?:data-original|data-src|src)="(?P<cover>[^"]+)")?',
    re.IGNORECASE | re.DOTALL,
)
JAVDB_PANEL_BLOCK_PATTERN = re.compile(
    r'<div[^>]+class="panel-block"[^>]*>.*?<strong>(?P<key>[^<]+)</strong>.*?'
    r'<(?:span|div)[^>]+class="value"[^>]*>(?P<value>.*?)</(?:span|div)>',
    re.IGNORECASE | re.DOTALL,
)
JAVDB_ACTOR_BLOCK_PATTERN = re.compile(
    r'<div[^>]+class="panel-block"[^>]*>.*?<strong>[^<]*演員[^<]*</strong>.*?'
    r'<(?:span|div)[^>]+class="value"[^>]*>(?P<value>.*?)</(?:span|div)>',
    re.IGNORECASE | re.DOTALL,
)
JAVDB_TAG_PATTERN = re.compile(r"<a[^>]*>(?P<tag>[^<]+)</a>", re.IGNORECASE)
JAVDB_CLEAN_TAG_PATTERN = re.compile(r"<[^>]+>")
JAVDB_RATING_PATTERN = re.compile(r"(?P<score>[\d.]+)\s*分")


@dataclass(frozen=True)
class _Detail:
    code: str
    title: str
    date: str
    studio: str
    series: str
    actors: list[str]
    tags: list[str]
    cover_url: str


def _clean_html_text(raw: str) -> str:
    text = JAVDB_CLEAN_TAG_PATTERN.sub("", raw or "")
    return text.replace("&nbsp;", " ").strip()


class JavdbProvider:
    name = "javdb"

    def __init__(
        self,
        *,
        base_url: str,
        timeout_sec: int,
        use_env_proxy: bool,
    ) -> None:
        self.base_url = (base_url or "https://javdb8.com/").strip()
        if not self.base_url.endswith("/"):
            self.base_url += "/"
        self.timeout_sec = max(1, timeout_sec)
        self.use_env_proxy = use_env_proxy

    def _http_get(self, url: str) -> tuple[int, str]:
        with requests.Session() as session:
            session.trust_env = self.use_env_proxy
            response = session.get(url, timeout=self.timeout_sec)
        return response.status_code, response.text

    def _parse_search_candidates(self, html: str) -> list[Candidate]:
        candidates: list[Candidate] = []
        for match in JAVDB_SEARCH_ITEM_PATTERN.finditer(html):
            href = match.group("href") or ""
            code = _clean_html_text(match.group("code") or "")
            title = _clean_html_text(match.group("title") or "")
            cover = (match.group("cover") or "").strip()
            if not href or not code:
                continue
            url = urljoin(self.base_url, href)
            if cover.startswith("//"):
                cover = f"https:{cover}"
            candidates.append(Candidate(code=code, url=url, title=title, cover=cover))
        return candidates

    def _parse_detail(self, html: str, *, url: str) -> _Detail | None:
        values: dict[str, str] = {}
        for match in JAVDB_PANEL_BLOCK_PATTERN.finditer(html):
            key = _clean_html_text(match.group("key"))
            value = _clean_html_text(match.group("value"))
            if key and value:
                values[key] = value

        code = values.get("番號") or values.get("番号") or ""
        title = ""
        title_match = re.search(
            r'<strong[^>]*>(?P<title>[^<]+)</strong>',
            html,
            re.IGNORECASE,
        )
        if title_match:
            title = _clean_html_text(title_match.group("title"))
        date = values.get("日期") or values.get("発売日") or ""
        studio = values.get("片商") or values.get("製作商") or ""
        series = values.get("系列") or ""

        actor_block = JAVDB_ACTOR_BLOCK_PATTERN.search(html)
        actors: list[str] = []
        if actor_block:
            raw_value = actor_block.group("value")
            names = [_clean_html_text(item) for item in raw_value.split(",")]
            actors = [name for name in names if name]

        tags: list[str] = []
        genre_raw = values.get("類別") or values.get("类别")
        if genre_raw:
            tags = [item.strip() for item in genre_raw.split(",") if item.strip()]

        cover = ""
        for pattern in (
            r'<img[^>]+class="video-cover"[^>]+data-original="(?P<img>[^"]+)"',
            r'<img[^>]+class="video-cover"[^>]+data-src="(?P<img>[^"]+)"',
            r'<img[^>]+class="video-cover"[^>]+src="(?P<img>[^"]+)"',
            r'<meta[^>]+property="og:image"[^>]+content="(?P<img>[^"]+)"',
        ):
            m = re.search(pattern, html, re.IGNORECASE)
            if m:
                cover = (m.group("img") or "").strip()
                break
        if cover.startswith("//"):
            cover = f"https:{cover}"
        if cover:
            cover = urljoin(self.base_url, cover)

        if not code:
            return None
        if title.startswith(code):
            title = title[len(code) :].strip()
        return _Detail(
            code=code,
            title=title,
            date=date,
            studio=studio,
            series=series,
            actors=actors,
            tags=tags,
            cover_url=cover,
        )

    def fetch_movie_info(self, movie_code: str, cfg: Config) -> ProviderFetchResult:
        del cfg
        query_keys = expand_query_keys(movie_code)
        errors: list[str] = []

        for key in query_keys:
            search_url = f"{self.base_url}search?q={quote(key)}&f=all"
            try:
                status, html = self._http_get(search_url)
            except Exception as exc:
                errors.append(f"search[{key}]: {exc}")
                continue
            if status == 404:
                continue
            if status >= 500:
                errors.append(f"search[{key}] status={status}")
                continue
            candidates = self._parse_search_candidates(html)
            chosen = select_best_candidate(movie_code, candidates)
            if chosen is None:
                continue

            try:
                detail_status, detail_html = self._http_get(chosen.url)
            except Exception as exc:
                errors.append(f"detail[{chosen.url}]: {exc}")
                continue
            if detail_status == 404:
                continue
            if detail_status >= 500:
                errors.append(f"detail[{chosen.url}] status={detail_status}")
                continue
            detail = self._parse_detail(detail_html, url=chosen.url)
            if detail is None:
                errors.append(f"detail[{chosen.url}] parse failed")
                continue

            return ProviderFetchResult(
                provider_name=self.name,
                status="success",
                movie=MovieInfo(
                    movie_id=movie_code,
                    title=detail.title or chosen.title,
                    actors=detail.actors,
                    tags=detail.tags,
                    cover_url=detail.cover_url or chosen.cover,
                    date=detail.date,
                    studio=detail.studio,
                    series=detail.series,
                ),
            )

        if errors:
            return ProviderFetchResult(
                provider_name=self.name,
                status="error",
                message=" | ".join(errors[:3]),
            )
        return ProviderFetchResult(
            provider_name=self.name,
            status="not_found",
            message=f"{movie_code} not found on {self.name}",
        )

