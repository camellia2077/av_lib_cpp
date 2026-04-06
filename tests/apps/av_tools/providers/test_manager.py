from dataclasses import dataclass

import pytest

from apps.av_tools.move_by_actor.app.config import Config
from apps.av_tools.move_by_actor.app.models import MovieInfo
from apps.av_tools.providers.base import ProviderFetchResult
from apps.av_tools.providers.manager import (
    ProviderChainError,
    ProviderManager,
    build_provider_manager_from_runtime,
)
from apps.av_tools.providers.runtime_options import (
    JavbusBrowserOptions,
    ProvidersRuntimeOptions,
)


@dataclass
class _FakeProvider:
    name: str
    result: ProviderFetchResult

    def fetch_movie_info(self, movie_code: str, cfg: Config) -> ProviderFetchResult:
        del movie_code
        del cfg
        return self.result


def test_provider_manager_fallbacks_to_next_provider_on_not_found() -> None:
    p1 = _FakeProvider(
        "p1",
        ProviderFetchResult(provider_name="p1", status="not_found", message="not found"),
    )
    p2 = _FakeProvider(
        "p2",
        ProviderFetchResult(
            provider_name="p2",
            status="success",
            movie=MovieInfo(movie_id="IPSD-048", title="ok", actors=["A"]),
        ),
    )
    manager = ProviderManager([p1, p2])

    result = manager.fetch_movie_info("IPSD-048", Config())

    assert result.provider_name == "p2"
    assert len(result.attempts) == 2
    assert result.attempts[0].status == "not_found"
    assert result.attempts[1].status == "success"


def test_provider_manager_raises_not_found_when_all_not_found() -> None:
    manager = ProviderManager(
        [
            _FakeProvider(
                "p1",
                ProviderFetchResult(
                    provider_name="p1", status="not_found", message="nf1"
                ),
            ),
            _FakeProvider(
                "p2",
                ProviderFetchResult(
                    provider_name="p2", status="not_found", message="nf2"
                ),
            ),
        ]
    )

    with pytest.raises(ProviderChainError) as exc:
        manager.fetch_movie_info("IPSD-048", Config())

    assert exc.value.kind == "not_found"
    assert len(exc.value.attempts) == 2


def test_provider_manager_raises_error_when_all_failed() -> None:
    manager = ProviderManager(
        [
            _FakeProvider(
                "p1",
                ProviderFetchResult(provider_name="p1", status="error", message="e1"),
            ),
            _FakeProvider(
                "p2",
                ProviderFetchResult(provider_name="p2", status="error", message="e2"),
            ),
        ]
    )

    with pytest.raises(ProviderChainError) as exc:
        manager.fetch_movie_info("IPSD-048", Config())

    assert exc.value.kind == "error"
    assert len(exc.value.attempts) == 2


def test_provider_manager_browser_on_error_only_runs_after_chain_failure() -> None:
    primary = _FakeProvider(
        "javdb",
        ProviderFetchResult(provider_name="javdb", status="not_found", message="nf"),
    )
    browser = _FakeProvider(
        "browser_fallback",
        ProviderFetchResult(
            provider_name="browser_fallback",
            status="success",
            movie=MovieInfo(movie_id="IPSD-048", title="browser-ok", actors=["A"]),
        ),
    )
    manager = ProviderManager(
        [primary],
        browser_fallback_provider=browser,
        browser_fallback_mode="on_error",
    )

    result = manager.fetch_movie_info("IPSD-048", Config())

    assert result.provider_name == "browser_fallback"
    assert len(result.attempts) == 2
    assert result.attempts[0].provider_name == "javdb"
    assert result.attempts[1].provider_name == "browser_fallback"


def test_provider_manager_browser_on_error_not_called_when_chain_succeeds() -> None:
    class _CountingProvider(_FakeProvider):
        calls = 0

        def fetch_movie_info(self, movie_code: str, cfg: Config) -> ProviderFetchResult:
            del movie_code
            del cfg
            self.calls += 1
            return self.result

    success_primary = _FakeProvider(
        "javdb",
        ProviderFetchResult(
            provider_name="javdb",
            status="success",
            movie=MovieInfo(movie_id="IPSD-048", title="ok", actors=["A"]),
        ),
    )
    browser = _CountingProvider(
        "browser_fallback",
        ProviderFetchResult(provider_name="browser_fallback", status="not_found"),
    )
    manager = ProviderManager(
        [success_primary],
        browser_fallback_provider=browser,
        browser_fallback_mode="on_error",
    )

    result = manager.fetch_movie_info("IPSD-048", Config())

    assert result.provider_name == "javdb"
    assert browser.calls == 0


def test_provider_manager_browser_always_runs_before_primary() -> None:
    primary = _FakeProvider(
        "javdb",
        ProviderFetchResult(
            provider_name="javdb",
            status="success",
            movie=MovieInfo(movie_id="IPSD-048", title="primary-ok", actors=["A"]),
        ),
    )
    browser = _FakeProvider(
        "browser_fallback",
        ProviderFetchResult(
            provider_name="browser_fallback",
            status="success",
            movie=MovieInfo(movie_id="IPSD-048", title="browser-ok", actors=["A"]),
        ),
    )
    manager = ProviderManager(
        [primary],
        browser_fallback_provider=browser,
        browser_fallback_mode="always",
    )

    result = manager.fetch_movie_info("IPSD-048", Config())

    assert result.provider_name == "browser_fallback"
    assert len(result.attempts) == 1
    assert result.attempts[0].provider_name == "browser_fallback"


def test_provider_manager_browser_only_can_run_without_primary_providers() -> None:
    browser = _FakeProvider(
        "browser_fallback",
        ProviderFetchResult(
            provider_name="browser_fallback",
            status="success",
            movie=MovieInfo(movie_id="IPSD-048", title="browser-only", actors=["A"]),
        ),
    )
    manager = ProviderManager(
        [],
        browser_fallback_provider=browser,
        browser_fallback_mode="only",
    )

    result = manager.fetch_movie_info("IPSD-048", Config())

    assert result.provider_name == "browser_fallback"
    assert len(result.attempts) == 1


def test_build_provider_manager_from_runtime_includes_javbus_browser_when_enabled() -> None:
    options = ProvidersRuntimeOptions(
        enabled=["javbus_browser", "javdb"],
        javbus_browser=JavbusBrowserOptions(enabled=True),
    )

    manager = build_provider_manager_from_runtime(options, use_env_proxy=False)

    assert [provider.name for provider in manager.providers] == ["javbus_browser", "javdb"]
