from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MovieInfo:
    movie_id: str
    title: str
    actors: list[str]
    tags: list[str] | None = None
    cover_url: str = ""
    date: str = ""
    studio: str = ""
    series: str = ""
