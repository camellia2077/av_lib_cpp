from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote, urljoin

from ..move_by_actor.app.config import Config
from ..move_by_actor.app.models import MovieInfo
from .base import ProviderFetchResult
from .utils import Candidate, expand_query_keys, select_best_candidate

JAVDB_CLEAN_TAG_PATTERN = re.compile(r"<[^>]+>")
R18_NUM_PATTERN = re.compile(r"([A-Z]{2,10})[-_ ]?(\d{2,6})", re.IGNORECASE)
R18_ID_PATTERN = re.compile(r"id=(?P<id>[a-z0-9]+)", re.IGNORECASE)


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


class BrowserFallbackProvider:
    name = "browser_fallback"

    def __init__(
        self,
        *,
        javdb_base_url: str,
        r18_base_url: str,
        headless: bool,
        nav_timeout_sec: float,
    ) -> None:
        self.javdb_base_url = (javdb_base_url or "https://javdb8.com/").strip()
        if not self.javdb_base_url.endswith("/"):
            self.javdb_base_url += "/"
        self.r18_base_url = (r18_base_url or "https://www.r18.com/").strip()
        if not self.r18_base_url.endswith("/"):
            self.r18_base_url += "/"
        self.headless = headless
        self.nav_timeout_ms = max(1000, int(nav_timeout_sec * 1000))

    @staticmethod
    def _clean_text(raw: str) -> str:
        text = JAVDB_CLEAN_TAG_PATTERN.sub("", raw or "")
        return text.replace("\xa0", " ").replace("&nbsp;", " ").strip()

    @staticmethod
    def _pick_attr(attrs: dict[str, str], keys: tuple[str, ...]) -> str:
        for key in keys:
            value = (attrs.get(key) or "").strip()
            if value:
                return value
        return ""

    def _browser_get(self, context, url: str) -> tuple[int, str]:
        page = context.new_page()
        try:
            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.nav_timeout_ms,
            )
            page.wait_for_timeout(250)
            status = response.status if response is not None else 0
            return status, page.content()
        finally:
            page.close()

    def _parse_javdb_search_candidates(self, html: str) -> list[Candidate]:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        candidates: list[Candidate] = []
        for anchor in soup.select("a[href^='/v/']"):
            href = (anchor.get("href") or "").strip()
            uid_node = anchor.select_one(".uid")
            if not href or uid_node is None:
                continue
            code = self._clean_text(uid_node.get_text(" ", strip=True))
            if not code:
                continue
            title_node = anchor.select_one(".video-title")
            title = self._clean_text(
                title_node.get_text(" ", strip=True) if title_node else ""
            )
            image_node = anchor.select_one("img")
            cover = ""
            if image_node is not None:
                cover = self._pick_attr(
                    image_node.attrs, ("data-original", "data-src", "src")
                )
            if cover.startswith("//"):
                cover = f"https:{cover}"
            if cover:
                cover = urljoin(self.javdb_base_url, cover)
            candidates.append(
                Candidate(
                    code=code,
                    url=urljoin(self.javdb_base_url, href),
                    title=title,
                    cover=cover,
                )
            )
        return candidates

    def _parse_javdb_detail(self, html: str) -> _Detail | None:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        values: dict[str, str] = {}
        for block in soup.select(".panel-block"):
            key_node = block.select_one("strong")
            value_node = block.select_one(".value")
            if key_node is None or value_node is None:
                continue
            key = self._clean_text(key_node.get_text(" ", strip=True))
            if not key:
                continue
            values[key] = self._clean_text(value_node.get_text(" ", strip=True))

        code = values.get("番號") or values.get("番号") or ""
        title = ""
        title_node = soup.select_one("h2.title strong") or soup.select_one("h2 strong")
        if title_node is not None:
            title = self._clean_text(title_node.get_text(" ", strip=True))

        date = values.get("日期") or values.get("発売日") or ""
        studio = values.get("片商") or values.get("製作商") or ""
        series = values.get("系列") or ""

        actors: list[str] = []
        for block in soup.select(".panel-block"):
            key_node = block.select_one("strong")
            value_node = block.select_one(".value")
            if key_node is None or value_node is None:
                continue
            key = self._clean_text(key_node.get_text(" ", strip=True))
            if "演員" not in key and "演员" not in key:
                continue
            actors = [
                self._clean_text(node.get_text(" ", strip=True))
                for node in value_node.select("a")
                if self._clean_text(node.get_text(" ", strip=True))
            ]
            if not actors:
                actors = [
                    name.strip()
                    for name in self._clean_text(value_node.get_text(" ", strip=True)).split(",")
                    if name.strip()
                ]
            break

        tags: list[str] = []
        for block in soup.select(".panel-block"):
            key_node = block.select_one("strong")
            value_node = block.select_one(".value")
            if key_node is None or value_node is None:
                continue
            key = self._clean_text(key_node.get_text(" ", strip=True))
            if key not in {"類別", "类别"}:
                continue
            tags = [
                self._clean_text(node.get_text(" ", strip=True))
                for node in value_node.select("a")
                if self._clean_text(node.get_text(" ", strip=True))
            ]
            if not tags:
                tags = [
                    item.strip()
                    for item in self._clean_text(value_node.get_text(" ", strip=True)).split(",")
                    if item.strip()
                ]
            break

        cover = ""
        cover_node = soup.select_one("img.video-cover")
        if cover_node is not None:
            cover = self._pick_attr(cover_node.attrs, ("data-original", "data-src", "src"))
        if not cover:
            meta = soup.select_one("meta[property='og:image']")
            if meta is not None:
                cover = (meta.get("content") or "").strip()
        if cover.startswith("//"):
            cover = f"https:{cover}"
        if cover:
            cover = urljoin(self.javdb_base_url, cover)

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

    def _parse_r18_search_candidates(self, html: str) -> list[Candidate]:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        candidates: list[Candidate] = []
        for anchor in soup.select("a[href*='/videos/vod/movies/detail/']"):
            href = (anchor.get("href") or "").strip()
            if not href:
                continue
            title = self._clean_text(anchor.get_text(" ", strip=True))
            if not title:
                continue
            code = ""
            match = R18_NUM_PATTERN.search(title)
            if match:
                code = f"{match.group(1).upper()}-{match.group(2)}"
            if not code:
                id_match = R18_ID_PATTERN.search(href)
                if id_match:
                    raw_id = id_match.group("id").upper()
                    id_code = R18_NUM_PATTERN.search(raw_id)
                    if id_code:
                        code = f"{id_code.group(1).upper()}-{id_code.group(2)}"
            if not code:
                continue
            candidates.append(
                Candidate(
                    code=code,
                    url=urljoin(self.r18_base_url, href),
                    title=title,
                )
            )
        return candidates

    def _parse_r18_detail(self, html: str, *, fallback_code: str) -> _Detail | None:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        title = ""
        title_node = soup.select_one('[itemprop="name"]')
        if title_node is not None:
            title = self._clean_text(title_node.get_text(" ", strip=True))

        code = fallback_code
        product_id = soup.select_one('[itemprop="productID"]')
        if product_id is not None:
            raw_id = self._clean_text(product_id.get_text(" ", strip=True))
            id_code = R18_NUM_PATTERN.search(raw_id)
            if id_code:
                code = f"{id_code.group(1).upper()}-{id_code.group(2)}"

        actors = [
            self._clean_text(node.get_text(" ", strip=True))
            for node in soup.select('[itemprop="actors"] [itemprop="name"]')
            if self._clean_text(node.get_text(" ", strip=True))
        ]
        tags = [
            self._clean_text(node.get_text(" ", strip=True))
            for node in soup.select('[itemprop="genre"]')
            if self._clean_text(node.get_text(" ", strip=True))
        ]

        date = ""
        date_node = soup.select_one('[itemprop="dateCreated"]')
        if date_node is not None:
            date = self._clean_text(date_node.get_text(" ", strip=True))

        cover = ""
        meta = soup.select_one("meta[property='og:image']")
        if meta is not None:
            cover = (meta.get("content") or "").strip()
        if not cover:
            img = soup.select_one("img.detail-single-picture")
            if img is not None:
                cover = (img.get("src") or "").strip()
        if cover.startswith("//"):
            cover = f"https:{cover}"
        if cover:
            cover = urljoin(self.r18_base_url, cover)

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

    def _fetch_via_javdb(self, movie_code: str, context) -> ProviderFetchResult:
        errors: list[str] = []
        for key in expand_query_keys(movie_code):
            search_url = f"{self.javdb_base_url}search?q={quote(key)}&f=all"
            try:
                status, html = self._browser_get(context, search_url)
            except Exception as exc:  # pragma: no cover - runtime/network dependent
                errors.append(f"search[{key}]: {exc}")
                continue
            if status >= 500:
                errors.append(f"search[{key}] status={status}")
                continue
            candidates = self._parse_javdb_search_candidates(html)
            chosen = select_best_candidate(movie_code, candidates)
            if chosen is None:
                continue
            try:
                detail_status, detail_html = self._browser_get(context, chosen.url)
            except Exception as exc:  # pragma: no cover - runtime/network dependent
                errors.append(f"detail[{chosen.url}]: {exc}")
                continue
            if detail_status >= 500:
                errors.append(f"detail[{chosen.url}] status={detail_status}")
                continue
            detail = self._parse_javdb_detail(detail_html)
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
            message=f"{movie_code} not found by browser on javdb",
        )

    def _fetch_via_r18(self, movie_code: str, context) -> ProviderFetchResult:
        errors: list[str] = []
        for key in expand_query_keys(movie_code):
            search_url = f"{self.r18_base_url}searchword={quote(key)}/"
            try:
                status, html = self._browser_get(context, search_url)
            except Exception as exc:  # pragma: no cover - runtime/network dependent
                errors.append(f"search[{key}]: {exc}")
                continue
            if status >= 500:
                errors.append(f"search[{key}] status={status}")
                continue
            candidates = self._parse_r18_search_candidates(html)
            chosen = select_best_candidate(movie_code, candidates)
            if chosen is None:
                continue
            try:
                detail_status, detail_html = self._browser_get(context, chosen.url)
            except Exception as exc:  # pragma: no cover - runtime/network dependent
                errors.append(f"detail[{chosen.url}]: {exc}")
                continue
            if detail_status >= 500:
                errors.append(f"detail[{chosen.url}] status={detail_status}")
                continue
            detail = self._parse_r18_detail(detail_html, fallback_code=chosen.code)
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
            message=f"{movie_code} not found by browser on r18",
        )

    def fetch_movie_info(self, movie_code: str, cfg: Config) -> ProviderFetchResult:
        del cfg
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:
            return ProviderFetchResult(
                provider_name=self.name,
                status="error",
                message=(
                    "playwright is unavailable. Install with "
                    "'pip install playwright beautifulsoup4' and "
                    "'python -m playwright install chromium'. "
                    f"detail={exc}"
                ),
            )

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=self.headless)
                try:
                    context = browser.new_context()
                    javdb_result = self._fetch_via_javdb(movie_code, context)
                    if javdb_result.status == "success":
                        return javdb_result
                    r18_result = self._fetch_via_r18(movie_code, context)
                    if r18_result.status == "success":
                        return r18_result

                    messages = [msg for msg in (javdb_result.message, r18_result.message) if msg]
                    status = (
                        "error"
                        if javdb_result.status == "error" or r18_result.status == "error"
                        else "not_found"
                    )
                    return ProviderFetchResult(
                        provider_name=self.name,
                        status=status,
                        message=" | ".join(messages[:3]),
                    )
                finally:
                    browser.close()
        except Exception as exc:  # pragma: no cover - runtime/browser dependent
            return ProviderFetchResult(
                provider_name=self.name,
                status="error",
                message=f"browser fetch failed: {exc}",
            )
