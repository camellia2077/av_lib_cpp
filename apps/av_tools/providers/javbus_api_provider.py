from __future__ import annotations

from ..move_by_actor.app.api_client import get_movie_info
from ..move_by_actor.app.config import Config
from .base import ProviderFetchResult


class JavbusApiProvider:
    name = "javbus_api"

    def fetch_movie_info(self, movie_code: str, cfg: Config) -> ProviderFetchResult:
        try:
            movie = get_movie_info(movie_code, cfg=cfg)
        except Exception as exc:
            message = str(exc)
            if "404" in message or "not found" in message.lower():
                return ProviderFetchResult(
                    provider_name=self.name,
                    status="not_found",
                    message=message,
                )
            return ProviderFetchResult(
                provider_name=self.name,
                status="error",
                message=message,
            )
        return ProviderFetchResult(
            provider_name=self.name,
            status="success",
            movie=movie,
        )
