from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MovieInfo:
    movie_id: str
    title: str
    actors: list[str]
