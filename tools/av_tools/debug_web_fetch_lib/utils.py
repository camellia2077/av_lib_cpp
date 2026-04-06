from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from urllib.parse import quote

from .models import CODE_PATTERN, ParseSiteName, SiteName

JAVBUS_UNCENSORED_CODE_PATTERN = re.compile(r"^\d{6}[-_]\d{2,4}$", re.IGNORECASE)


def normalize_code(raw: str) -> str:
    text = (raw or "").strip().upper()
    match = CODE_PATTERN.search(text)
    if match:
        return match.group(0).upper()

    # Keep vendor-specific canonical formats recognizable in debug reports.
    # - TOKYO-HOT-N1039
    # - HEYZO-0904
    for pattern in (
        r"(TOKYO-HOT-[A-Z]\d{4})",
        r"(HEYZO-\d{4})",
        r"(\d{6}-\d{2,4})-CARIB",
        r"(\d{6}_\d{3})-1PONDO",
        r"(\d{6}-\d{2,4})",
        r"(\d{6}_\d{3})",
    ):
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).upper() if m.lastindex else m.group(0).upper()
    return ""


def clean_text(raw: str) -> str:
    return re.sub(r"\s+", " ", (raw or "").replace("\xa0", " ").strip())


def detect_block_markers(html: str, title: str, status: int) -> list[str]:
    text = f"{title}\n{html[:12000]}".lower()
    markers: list[str] = []
    if status == 403:
        markers.append("status_403")
    if "cloudflare" in text or "attention required" in text:
        markers.append("cloudflare")
    if "captcha" in text or "verify you are human" in text:
        markers.append("captcha")
    if "driver-verify" in text or "age verification" in text:
        markers.append("age_verification")
    if "over18" in text or "我已滿18歲" in text or "我已满18岁" in text:
        markers.append("over18_gate")
    return markers


def infer_parse_site(site: SiteName, base_url: str, parse_as: str | None) -> ParseSiteName:
    if parse_as is not None:
        if parse_as in {"javdb", "javbus", "r18", "none"}:
            return parse_as  # type: ignore[return-value]
        raise ValueError("Invalid --parse-as, choose javdb|javbus|r18|none")

    if site != "custom":
        return site  # type: ignore[return-value]

    lower = base_url.lower()
    if "javdb" in lower:
        return "javdb"
    if "javbus" in lower:
        return "javbus"
    if "r18" in lower:
        return "r18"
    return "none"


def build_url(site: SiteName, code: str, base_url: str) -> str:
    base = base_url.strip()
    if site == "custom":
        if "{code}" not in base:
            raise ValueError("custom --base-url must contain '{code}' placeholder")
        return base.format(code=quote(code))
    if not base.endswith("/"):
        base += "/"
    if site == "javdb":
        return f"{base}search?q={quote(code)}&f=all"
    if site == "javbus":
        # Uncensored/date-based ids on JavBus are indexed under
        # /uncensored/search/ rather than /search/.
        if JAVBUS_UNCENSORED_CODE_PATTERN.fullmatch(code):
            return f"{base}uncensored/search/{quote(code)}"
        return f"{base}search/{quote(code)}"
    if site == "r18":
        return f"{base}searchword={quote(code)}/"
    raise ValueError(f"Unsupported site: {site}")


def save_html(output_dir: Path, prefix: str, html: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"{prefix}_{timestamp}.html"
    path.write_text(html, encoding="utf-8", errors="ignore")
    return path
