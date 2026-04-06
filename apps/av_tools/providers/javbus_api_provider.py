from __future__ import annotations

from ..move_by_actor.app.api_client import get_movie_info
from ..move_by_actor.app.config import Config
from ..move_by_actor.app.models import MovieInfo


class JavbusApiProvider:
    name = "javbus_api"

    def fetch_movie_info(self, movie_code: str, cfg: Config) -> MovieInfo:
        return get_movie_info(movie_code, cfg=cfg)

