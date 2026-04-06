from __future__ import annotations

from dataclasses import dataclass

from ..move_by_actor.app.config import Config
from ..move_by_actor.app.models import MovieInfo
from .base import MetadataProvider, ProviderResult
from .javbus_api_provider import JavbusApiProvider


@dataclass(frozen=True)
class ProviderError:
    provider_name: str
    error: Exception


class ProviderManager:
    def __init__(self, providers: list[MetadataProvider]) -> None:
        if not providers:
            raise ValueError("At least one provider is required.")
        self.providers = providers

    def fetch_movie_info(self, movie_code: str, cfg: Config) -> ProviderResult:
        errors: list[ProviderError] = []
        for provider in self.providers:
            try:
                movie = provider.fetch_movie_info(movie_code, cfg)
                return ProviderResult(provider_name=provider.name, movie=movie)
            except Exception as exc:
                errors.append(ProviderError(provider_name=provider.name, error=exc))

        details = "; ".join(f"{item.provider_name}: {item.error}" for item in errors)
        raise RuntimeError(f"All providers failed for {movie_code}. {details}")


def build_default_provider_manager() -> ProviderManager:
    # First version uses javbus-api only. Additional providers can be
    # registered here later without changing fetch-metadata workflow.
    return ProviderManager(providers=[JavbusApiProvider()])

