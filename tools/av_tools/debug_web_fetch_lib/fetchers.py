from __future__ import annotations

import re

import requests

from .models import DEFAULT_HEADERS
from .utils import clean_text


def fetch_requests(url: str, timeout: float, use_env_proxy: bool) -> tuple[int, str, str, str]:
    with requests.Session() as session:
        session.trust_env = use_env_proxy
        response = session.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers=DEFAULT_HEADERS,
        )

    title_match = re.search(
        r"<title[^>]*>(.*?)</title>",
        response.text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    title = clean_text(title_match.group(1)) if title_match else ""
    return response.status_code, response.text, response.url, title


def fetch_browser(url: str, timeout: float, show_browser: bool) -> tuple[int, str, str, str]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise RuntimeError(
            "playwright unavailable, run: pip install playwright && python -m playwright install chromium"
        ) from exc

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not show_browser)
        try:
            context = browser.new_context(
                user_agent=DEFAULT_HEADERS["User-Agent"],
                locale="zh-CN",
            )
            page = context.new_page()
            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=max(1000, int(timeout * 1000)),
            )
            try:
                page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                pass
            html = page.content()
            title = clean_text(page.title())
            status = response.status if response is not None else 0
            return status, html, page.url, title
        finally:
            browser.close()
