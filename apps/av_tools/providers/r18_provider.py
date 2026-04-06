from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote, urljoin

import requests

from ..move_by_actor.app.config import Config
from ..move_by_actor.app.models import MovieInfo
from .base import ProviderFetchResult
from .utils import Candidate, expand_query_keys, select_best_candidate

R18_SEARCH_ITEM_PATTERN = re.compile(
    r'<a[^>]+href="(?P<href>/videos/vod/movies/detail/[^"]+id=[^"]+)"[^>]*>.*?'
    r'<span[^>]*>(?P<title>[^<]+)</span>',
    re.IGNORECASE | re.DOTALL,
)
R18_ID_PATTERN = re.compile(r"id=(?P<id>[a-z0-9]+)", re.IGNORECASE)
R18_NUM_PATTERN = re.compile(r"([A-Z]{2,10})[-_ ]?(\d{2,6})", re.IGNORECASE)
R18_CLEAN_TAG_PATTERN = re.compile(r"<[^>]+>")


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


def _clean(raw: str) -> str:
    return R18_CLEAN_TAG_PATTERN.sub("", raw or "").replace("&nbsp;", " ").strip()


class R18Provider:
    name = "r18"

    def __init__(
        self,
        *,
        base_url: str,
        timeout_sec: int,
        use_env_proxy: bool,
    ) -> None:
        self.base_url = (base_url or "https://www.r18.com/").strip()
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
        results: list[Candidate] = []
        for match in R18_SEARCH_ITEM_PATTERN.finditer(html):
            href = match.group("href") or ""
            title = _clean(match.group("title") or "")
            url = urljoin(self.base_url, href)
            code = ""
            code_match = R18_NUM_PATTERN.search(title)
            if code_match:
                code = f"{code_match.group(1).upper()}-{code_match.group(2)}"
            else:
                id_match = R18_ID_PATTERN.search(href)
                if id_match:
                    raw_id = id_match.group("id").upper()
                    code_match = R18_NUM_PATTERN.search(raw_id)
                    if code_match:
                        code = f"{code_match.group(1).upper()}-{code_match.group(2)}"
            if not code:
                continue
            results.append(Candidate(code=code, url=url, title=title))
        return results

    def _parse_detail(self, html: str, *, fallback_code: str) -> _Detail | None:
        title = ""
        m_title = re.search(
            r'<h1[^>]*itemprop="name"[^>]*>(?P<title>.*?)</h1>',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if m_title:
            title = _clean(m_title.group("title"))

        code = fallback_code
        m_id = re.search(
            r'<span[^>]*itemprop="productID"[^>]*>(?P<id>.*?)</span>',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if m_id:
            raw_id = _clean(m_id.group("id"))
            m_num = R18_NUM_PATTERN.search(raw_id)
            if m_num:
                code = f"{m_num.group(1).upper()}-{m_num.group(2)}"

        actors = [
            _clean(value)
            for value in re.findall(
                r'<[^>]*itemprop="actors"[^>]*>.*?<[^>]*itemprop="name"[^>]*>(.*?)</',
                html,
                re.IGNORECASE | re.DOTALL,
            )
            if _clean(value)
        ]
        tags = [
            _clean(value)
            for value in re.findall(
                r'<[^>]*itemprop="genre"[^>]*>(.*?)</',
                html,
                re.IGNORECASE | re.DOTALL,
            )
            if _clean(value)
        ]
        date = ""
        m_date = re.search(
            r'<[^>]*itemprop="dateCreated"[^>]*>(.*?)</',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if m_date:
            date = _clean(m_date.group(1))
        cover = ""
        for pattern in (
            r'<meta[^>]+property="og:image"[^>]+content="(?P<img>[^"]+)"',
            r'<img[^>]+class="[^"]*detail-single-picture[^"]*"[^>]+src="(?P<img>[^"]+)"',
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
            studio="",
            series="",
            actors=actors,
            tags=tags,
            cover_url=cover,
        )

    def fetch_movie_info(self, movie_code: str, cfg: Config) -> ProviderFetchResult:
        del cfg
        query_keys = expand_query_keys(movie_code)
        errors: list[str] = []
        for key in query_keys:
            search_url = f"{self.base_url}searchword={quote(key)}/"
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
            detail = self._parse_detail(detail_html, fallback_code=chosen.code)
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

