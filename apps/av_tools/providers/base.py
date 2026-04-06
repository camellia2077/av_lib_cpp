from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..move_by_actor.app.config import Config
from ..move_by_actor.app.models import MovieInfo


@dataclass(frozen=True)
class ProviderResult:
    provider_name: str
    movie: MovieInfo


class MetadataProvider(Protocol):
    name: str

    def fetch_movie_info(self, movie_code: str, cfg: Config) -> MovieInfo:
        ...

