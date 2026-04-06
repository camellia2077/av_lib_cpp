from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote, urljoin

from ..move_by_actor.app.config import Config
from ..move_by_actor.app.models import MovieInfo
from .base import ProviderFetchResult
from .utils import Candidate, expand_query_keys, select_best_candidate

JAVBUS_CLEAN_TAG_PATTERN = re.compile(r"<[^>]+>")
JAVBUS_CODE_PATTERN = re.compile(r"[A-Z]{2,10}-\d{2,6}", re.IGNORECASE)
# JavBus can route automation-like contexts to Age Verification pages if the
# browser context looks too generic. Keep UA/locale aligned with our probe tool.
DEFAULT_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_BROWSER_LOCALE = "zh-CN"


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


class JavbusBrowserProvider:
    name = "javbus_browser"

    def __init__(
        self,
        *,
        base_url: str,
        headless: bool,
        nav_timeout_sec: float,
    ) -> None:
        self.base_url = (base_url or "https://www.javbus.com/").strip()
        if not self.base_url.endswith("/"):
            self.base_url += "/"
        self.headless = headless
        self.nav_timeout_ms = max(1000, int(nav_timeout_sec * 1000))

    @staticmethod
    def _clean(raw: str) -> str:
        text = JAVBUS_CLEAN_TAG_PATTERN.sub("", raw or "")
        return text.replace("\xa0", " ").replace("&nbsp;", " ").strip()

    @staticmethod
    def _normalize_code(raw: str) -> str:
        match = JAVBUS_CODE_PATTERN.search((raw or "").upper())
        return match.group(0).upper() if match else ""

    @staticmethod
    def _safe_page_content(page, retries: int = 3) -> str:
        last_error: Exception | None = None
        for _ in range(max(1, retries)):
            try:
                return page.content()
            except Exception as exc:  # pragma: no cover - runtime/browser dependent
                last_error = exc
                page.wait_for_timeout(350)
        if last_error is not None:
            raise last_error
        return ""

    @staticmethod
    def _detect_block_reason(html: str, title: str, status: int) -> str:
        content = f"{title}\n{html[:8000]}".lower()
        if status == 403:
            return "status=403"
        # When we land on /doc/driver-verify, parsing candidates is impossible.
        if "age verification javbus" in content or "driver-verify" in content:
            return "age_verification"
        if "cloudflare" in content or "attention required" in content:
            return "cloudflare"
        if "captcha" in content or "verify you are human" in content:
            return "captcha"
        if "access denied" in content or "forbidden" in content:
            return "forbidden"
        return ""

    def _browser_get(self, context, url: str) -> tuple[int, str, str, str]:
        page = context.new_page()
        try:
            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.nav_timeout_ms,
            )
            try:
                page.wait_for_load_state("networkidle", timeout=min(3000, self.nav_timeout_ms))
            except Exception:
                pass
            html = self._safe_page_content(page)
            status = response.status if response is not None else 0
            title = page.title().strip() if page.title() else ""
            return status, html, page.url, title
        finally:
            page.close()

    def _parse_search_candidates(self, html: str) -> list[Candidate]:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        results: list[Candidate] = []
        for anchor in soup.select("a.movie-box"):
            href = (anchor.get("href") or "").strip()
            if not href:
                continue

            date_node = anchor.select_one("date")
            code = self._normalize_code(date_node.get_text(" ", strip=True) if date_node else "")
            if not code:
                code = self._normalize_code(anchor.get_text(" ", strip=True))
            if not code:
                continue

            image = anchor.select_one("img")
            title = ""
            cover = ""
            if image is not None:
                title = (image.get("title") or image.get("alt") or "").strip()
                cover = (image.get("src") or image.get("data-src") or "").strip()

            if cover:
                cover = urljoin(self.base_url, cover)

            results.append(
                Candidate(
                    code=code,
                    url=urljoin(self.base_url, href),
                    title=self._clean(title),
                    cover=cover,
                )
            )
        return results

    def _extract_info_value(self, info_root, labels: list[str]) -> str:
        for paragraph in info_root.select("p"):
            header = paragraph.select_one("span.header")
            if header is None:
                continue
            label = self._clean(header.get_text(" ", strip=True)).replace(":", "")
            if label not in labels:
                continue

            links = [self._clean(node.get_text(" ", strip=True)) for node in paragraph.select("a")]
            links = [item for item in links if item]
            if links:
                return links[0]

            raw = self._clean(paragraph.get_text(" ", strip=True))
            raw = raw.replace(self._clean(header.get_text(" ", strip=True)), "").strip(": ").strip()
            return raw
        return ""

    def _parse_detail(self, html: str, *, url: str) -> _Detail | None:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        title = ""
        title_node = soup.select_one("h3")
        if title_node is not None:
            title = self._clean(title_node.get_text(" ", strip=True))

        info_root = soup.select_one(".col-md-3.info")
        if info_root is None:
            return None

        code = self._extract_info_value(info_root, ["識別碼", "识别码", "ID"])
        if not code:
            code = self._normalize_code(url)

        date = self._extract_info_value(info_root, ["發行日期", "发行日期", "日期"])
        studio = self._extract_info_value(info_root, ["製作商", "制作商", "發行商", "发行商"])
        series = self._extract_info_value(info_root, ["系列"])

        actors = [
            self._clean(node.get_text(" ", strip=True))
            for node in soup.select(".star-name a")
            if self._clean(node.get_text(" ", strip=True))
        ]

        tags = [
            self._clean(node.get_text(" ", strip=True))
            for node in soup.select("span.genre a")
            if self._clean(node.get_text(" ", strip=True))
        ]

        cover = ""
        big_image = soup.select_one("a.bigImage")
        if big_image is not None:
            cover = (big_image.get("href") or "").strip()
        if not cover:
            cover_img = soup.select_one("a.bigImage img") or soup.select_one("img[src*='/pics/cover/']")
            if cover_img is not None:
                cover = (cover_img.get("src") or "").strip()
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

    def _fetch_with_context(self, movie_code: str, context) -> ProviderFetchResult:
        errors: list[str] = []
        # Space variants like "IPSD 048" are much more likely to hit 403 on
        # JavBus path search. Skip them to avoid noisy false failures.
        query_keys = [key for key in expand_query_keys(movie_code) if " " not in key]
        for key in query_keys:
            search_url = f"{self.base_url}search/{quote(key)}"
            try:
                status, html, final_url, title = self._browser_get(context, search_url)
            except KeyboardInterrupt:
                raise
            except Exception as exc:  # pragma: no cover - runtime/browser dependent
                errors.append(f"search[{key}]: {exc}")
                continue

            block_reason = self._detect_block_reason(html, title, status)
            if block_reason:
                errors.append(f"search[{key}] blocked={block_reason} url={final_url}")
                if block_reason in {"status=403", "age_verification", "cloudflare", "captcha"}:
                    break
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
                detail_status, detail_html, detail_url, detail_title = self._browser_get(
                    context,
                    chosen.url,
                )
            except KeyboardInterrupt:
                raise
            except Exception as exc:  # pragma: no cover - runtime/browser dependent
                errors.append(f"detail[{chosen.url}]: {exc}")
                continue

            detail_block_reason = self._detect_block_reason(detail_html, detail_title, detail_status)
            if detail_block_reason:
                errors.append(f"detail[{chosen.url}] blocked={detail_block_reason} url={detail_url}")
                if detail_block_reason in {"status=403", "age_verification", "cloudflare", "captcha"}:
                    break
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
                    context = browser.new_context(
                        user_agent=DEFAULT_BROWSER_USER_AGENT,
                        locale=DEFAULT_BROWSER_LOCALE,
                    )
                    return self._fetch_with_context(movie_code, context)
                finally:
                    browser.close()
        except KeyboardInterrupt:
            raise
        except Exception as exc:  # pragma: no cover - runtime/browser dependent
            return ProviderFetchResult(
                provider_name=self.name,
                status="error",
                message=f"browser fetch failed: {exc}",
            )
