from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

FailureReason = Literal["INVALID_INPUT", "NO_CODE", "API_ERROR", "NOT_FOUND"]


@dataclass(frozen=True)
class MetadataRecord:
    file_path: str
    movie_code: str
    title: str
    actors: list[str]
    tags: list[str]
    cover_url: str
    date: str = ""
    studio: str = ""
    series: str = ""
    provider: str = ""
    provider_attempts: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class MetadataFailure:
    file_path: str
    reason: FailureReason
    message: str
    movie_code: str = ""
    provider_attempts: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class FetchSummary:
    scanned_files: int
    success_count: int
    failed_count: int
    api_queries: int
    api_cache_hits: int
