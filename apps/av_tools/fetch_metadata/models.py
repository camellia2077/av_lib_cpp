from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FailureReason = Literal["INVALID_INPUT", "NO_CODE", "API_ERROR"]


@dataclass(frozen=True)
class MetadataRecord:
    file_path: str
    movie_code: str
    title: str
    actors: list[str]
    tags: list[str]
    cover_url: str


@dataclass(frozen=True)
class MetadataFailure:
    file_path: str
    reason: FailureReason
    message: str
    movie_code: str = ""


@dataclass(frozen=True)
class FetchSummary:
    scanned_files: int
    success_count: int
    failed_count: int
    api_queries: int
    api_cache_hits: int
