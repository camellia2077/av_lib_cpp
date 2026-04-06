from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

DEFAULT_BASE_URLS = {
    "javdb": "https://javdb8.com/",
    "javbus": "https://www.javbus.com/",
    "r18": "https://www.r18.com/",
}

SiteName = Literal["javdb", "javbus", "r18", "custom"]
ParseSiteName = Literal["javdb", "javbus", "r18", "none"]
ProbeMode = Literal["requests", "browser", "both"]

CODE_PATTERN = re.compile(r"[A-Z]{2,10}-\d{2,6}", re.IGNORECASE)


@dataclass(frozen=True)
class Candidate:
    code: str
    title: str
    url: str
    cover_url: str
