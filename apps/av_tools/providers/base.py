from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from ..move_by_actor.app.config import Config
from ..move_by_actor.app.models import MovieInfo

ProviderStatus = Literal["success", "not_found", "error"]


@dataclass(frozen=True)
class ProviderAttempt:
    provider_name: str
    status: ProviderStatus
    message: str = ""


@dataclass(frozen=True)
class ProviderFetchResult:
    provider_name: str
    status: ProviderStatus
    movie: MovieInfo | None = None
    message: str = ""


@dataclass(frozen=True)
class ProviderResult:
    provider_name: str
    movie: MovieInfo
    attempts: list[ProviderAttempt]


class MetadataProvider(Protocol):
    name: str

    def fetch_movie_info(self, movie_code: str, cfg: Config) -> ProviderFetchResult:
        ...
