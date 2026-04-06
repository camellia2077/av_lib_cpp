from __future__ import annotations

from urllib.parse import urljoin

from .models import Candidate, ParseSiteName
from .utils import clean_text, normalize_code


def parse_javdb_candidates(html: str, base_url: str) -> list[Candidate]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    candidates: list[Candidate] = []

    for anchor in soup.select(".movie-list a.box[href^='/v/']"):
        href = (anchor.get("href") or "").strip()
        if not href:
            continue
        url = urljoin(base_url, href)
        if url in seen:
            continue
        seen.add(url)

        title_node = anchor.select_one(".video-title")
        code_node = title_node.select_one("strong") if title_node else None
        code = normalize_code(code_node.get_text(" ", strip=True) if code_node else "")
        title_text = clean_text(title_node.get_text(" ", strip=True) if title_node else "")
        if code and title_text.upper().startswith(code):
            title_text = title_text[len(code) :].strip()

        image = anchor.select_one("img")
        cover = ""
        if image is not None:
            cover = (
                (image.get("data-original") or "")
                or (image.get("data-src") or "")
                or (image.get("src") or "")
            ).strip()
        if cover:
            cover = urljoin(base_url, cover)

        if code:
            candidates.append(Candidate(code=code, title=title_text, url=url, cover_url=cover))

    for anchor in soup.select("a[href^='/v/']"):
        href = (anchor.get("href") or "").strip()
        uid = anchor.select_one(".uid")
        if not href or uid is None:
            continue
        url = urljoin(base_url, href)
        if url in seen:
            continue
        seen.add(url)

        code = normalize_code(uid.get_text(" ", strip=True))
        if not code:
            continue
        title_node = anchor.select_one(".video-title")
        title_text = clean_text(title_node.get_text(" ", strip=True) if title_node else "")
        if title_text.upper().startswith(code):
            title_text = title_text[len(code) :].strip()

        image = anchor.select_one("img")
        cover = ""
        if image is not None:
            cover = (
                (image.get("data-original") or "")
                or (image.get("data-src") or "")
                or (image.get("src") or "")
            ).strip()
        if cover:
            cover = urljoin(base_url, cover)

        candidates.append(Candidate(code=code, title=title_text, url=url, cover_url=cover))

    return candidates


def parse_javbus_candidates(html: str, base_url: str) -> list[Candidate]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    candidates: list[Candidate] = []
    for anchor in soup.select("a.movie-box"):
        href = (anchor.get("href") or "").strip()
        if not href:
            continue
        date_node = anchor.select_one("date")
        code = normalize_code(date_node.get_text(" ", strip=True) if date_node else "")
        if not code:
            code = normalize_code(anchor.get_text(" ", strip=True))
        if not code:
            continue

        image = anchor.select_one("img")
        title = ""
        cover = ""
        if image is not None:
            title = clean_text((image.get("title") or image.get("alt") or "").strip())
            cover = ((image.get("src") or "") or (image.get("data-src") or "")).strip()
        if cover:
            cover = urljoin(base_url, cover)

        candidates.append(
            Candidate(
                code=code,
                title=title,
                url=urljoin(base_url, href),
                cover_url=cover,
            )
        )
    return candidates


def parse_r18_candidates(html: str, base_url: str) -> list[Candidate]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    candidates: list[Candidate] = []
    for anchor in soup.select("a[href*='/videos/vod/movies/detail/']"):
        href = (anchor.get("href") or "").strip()
        if not href:
            continue
        title = clean_text(anchor.get_text(" ", strip=True))
        code = normalize_code(title) or normalize_code(href)
        if not code:
            continue
        candidates.append(
            Candidate(
                code=code,
                title=title,
                url=urljoin(base_url, href),
                cover_url="",
            )
        )
    return candidates


def parse_candidates(site: ParseSiteName, html: str, base_url: str) -> list[Candidate]:
    if site == "javdb":
        return parse_javdb_candidates(html, base_url)
    if site == "javbus":
        return parse_javbus_candidates(html, base_url)
    if site == "r18":
        return parse_r18_candidates(html, base_url)
    return []
