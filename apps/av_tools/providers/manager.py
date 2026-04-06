from __future__ import annotations

from dataclasses import dataclass

from ..move_by_actor.app.config import Config
from .base import (
    MetadataProvider,
    ProviderAttempt,
    ProviderFetchResult,
    ProviderResult,
)
from .browser_fallback_provider import BrowserFallbackProvider
from .javbus_browser_provider import JavbusBrowserProvider
from .javbus_api_provider import JavbusApiProvider
from .javdb_provider import JavdbProvider
from .r18_provider import R18Provider
from .runtime_options import BrowserFallbackMode, ProvidersRuntimeOptions


@dataclass(frozen=True)
class ProviderChainError(RuntimeError):
    attempts: list[ProviderAttempt]
    kind: str

    def __str__(self) -> str:
        details = "; ".join(
            f"{attempt.provider_name}:{attempt.status}:{attempt.message}"
            for attempt in self.attempts
        )
        return details


class ProviderManager:
    def __init__(
        self,
        providers: list[MetadataProvider],
        *,
        browser_fallback_provider: MetadataProvider | None = None,
        browser_fallback_mode: BrowserFallbackMode = "off",
    ) -> None:
        if not providers and not (
            browser_fallback_provider is not None
            and browser_fallback_mode in {"always", "only"}
        ):
            raise ValueError("At least one provider is required.")
        self.providers = providers
        self.browser_fallback_provider = browser_fallback_provider
        self.browser_fallback_mode = browser_fallback_mode

    def fetch_movie_info(self, movie_code: str, cfg: Config) -> ProviderResult:
        attempts: list[ProviderAttempt] = []
        has_error = False

        def run_provider(provider: MetadataProvider) -> ProviderFetchResult:
            result = provider.fetch_movie_info(movie_code, cfg)
            attempts.append(
                ProviderAttempt(
                    provider_name=result.provider_name,
                    status=result.status,
                    message=result.message,
                )
            )
            return result

        if (
            self.browser_fallback_mode in {"always", "only"}
            and self.browser_fallback_provider is not None
        ):
            browser_result = run_provider(self.browser_fallback_provider)
            if browser_result.status == "success" and browser_result.movie is not None:
                return ProviderResult(
                    provider_name=browser_result.provider_name,
                    movie=browser_result.movie,
                    attempts=attempts,
                )
            if browser_result.status == "error":
                has_error = True
            if self.browser_fallback_mode == "only":
                if has_error:
                    raise ProviderChainError(attempts=attempts, kind="error")
                raise ProviderChainError(attempts=attempts, kind="not_found")

        for provider in self.providers:
            result = run_provider(provider)
            if result.status == "success" and result.movie is not None:
                return ProviderResult(
                    provider_name=result.provider_name,
                    movie=result.movie,
                    attempts=attempts,
                )
            if result.status == "error":
                has_error = True

        if (
            self.browser_fallback_mode == "on_error"
            and self.browser_fallback_provider is not None
        ):
            browser_result = run_provider(self.browser_fallback_provider)
            if browser_result.status == "success" and browser_result.movie is not None:
                return ProviderResult(
                    provider_name=browser_result.provider_name,
                    movie=browser_result.movie,
                    attempts=attempts,
                )
            if browser_result.status == "error":
                has_error = True

        if has_error:
            raise ProviderChainError(attempts=attempts, kind="error")
        raise ProviderChainError(attempts=attempts, kind="not_found")


def build_provider_manager_from_runtime(
    options: ProvidersRuntimeOptions,
    *,
    use_env_proxy: bool,
) -> ProviderManager:
    providers: list[MetadataProvider] = []
    mapping: dict[str, MetadataProvider] = {
        "javdb": JavdbProvider(
            base_url=options.javdb.base_url,
            timeout_sec=options.network.timeout_sec,
            use_env_proxy=use_env_proxy,
        ),
        "javbus_api": JavbusApiProvider(),
        "r18": R18Provider(
            base_url=options.r18.base_url,
            timeout_sec=options.network.timeout_sec,
            use_env_proxy=use_env_proxy,
        ),
        "javbus_browser": JavbusBrowserProvider(
            base_url=options.javbus_browser.base_url,
            headless=options.javbus_browser.headless,
            nav_timeout_sec=options.javbus_browser.nav_timeout_sec,
        ),
    }
    enabled_flags = {
        "javdb": options.javdb.enabled,
        "javbus_api": options.javbus_api.enabled,
        "r18": options.r18.enabled,
        "javbus_browser": options.javbus_browser.enabled,
    }
    for name in options.enabled:
        provider = mapping.get(name)
        if provider is None:
            continue
        if not enabled_flags.get(name, True):
            continue
        providers.append(provider)

    if not providers and options.browser_fallback.mode != "only":
        providers = [mapping["javbus_api"]]

    browser_fallback_provider: MetadataProvider | None = None
    if options.browser_fallback.mode in {"on_error", "always", "only"}:
        browser_fallback_provider = BrowserFallbackProvider(
            javdb_base_url=options.javdb.base_url,
            r18_base_url=options.r18.base_url,
            headless=options.browser_fallback.headless,
            nav_timeout_sec=options.browser_fallback.nav_timeout_sec,
        )

    return ProviderManager(
        providers=providers,
        browser_fallback_provider=browser_fallback_provider,
        browser_fallback_mode=options.browser_fallback.mode,
    )


def build_default_provider_manager() -> ProviderManager:
    return build_provider_manager_from_runtime(
        ProvidersRuntimeOptions(),
        use_env_proxy=True,
    )
