from pathlib import Path

from apps.av_tools.fetch_metadata import service
from apps.av_tools.fetch_metadata.models import MetadataFailure
from apps.av_tools.move_by_actor.app.config import Config
from apps.av_tools.move_by_actor.app.models import MovieInfo
from apps.av_tools.providers.base import ProviderAttempt


class _FakeProviderResult:
    def __init__(self, movie: MovieInfo, provider_name: str = "fake_provider") -> None:
        self.movie = movie
        self.provider_name = provider_name
        self.attempts = [
            ProviderAttempt(
                provider_name=provider_name,
                status="success",
                message="",
            )
        ]


class _FakeProviderManager:
    def __init__(self, fn):
        self._fn = fn

    def fetch_movie_info(self, movie_code: str, cfg: Config):
        return _FakeProviderResult(self._fn(movie_code, cfg))


def test_fetch_metadata_reuses_api_cache(tmp_path: Path, monkeypatch) -> None:
    file_a = tmp_path / "ABC-123.mp4"
    file_b = tmp_path / "abc123-copy.mkv"
    file_a.write_text("x", encoding="utf-8")
    file_b.write_text("x", encoding="utf-8")
    monkeypatch.setattr(
        service,
        "collect_video_files",
        lambda _path: ([file_a, file_b], []),
    )

    calls: list[str] = []

    def fake_get_movie_info(code: str, cfg: Config) -> MovieInfo:
        del cfg
        calls.append(code)
        return MovieInfo(
            movie_id=code,
            title="sample",
            actors=["actor"],
            tags=["tagA", "tagB"],
            cover_url="https://example.com/cover.jpg",
        )

    records, failures, summary = service.fetch_metadata(
        tmp_path,
        Config(),
        provider_manager=_FakeProviderManager(fake_get_movie_info),
    )

    assert len(records) == 1
    assert failures == []
    assert summary.api_queries == 1
    assert summary.api_cache_hits == 1
    assert calls == ["ABC-123"]


def test_fetch_metadata_sleeps_once_per_new_movie_code(tmp_path: Path, monkeypatch) -> None:
    file_a = tmp_path / "ABC-123.mp4"
    file_b = tmp_path / "ABC-123-CD1.mkv"
    file_c = tmp_path / "IPTD-908.mp4"
    for path in (file_a, file_b, file_c):
        path.write_text("x", encoding="utf-8")
    monkeypatch.setattr(
        service,
        "collect_video_files",
        lambda _path: ([file_a, file_b, file_c], []),
    )
    def fake_get_movie_info(code: str, cfg: Config) -> MovieInfo:
        del cfg
        return MovieInfo(
            movie_id=code,
            title="sample",
            actors=["actor"],
            tags=[],
            cover_url="",
        )
    sleeps: list[float] = []
    monkeypatch.setattr(service.time, "sleep", lambda sec: sleeps.append(sec))

    records, failures, summary = service.fetch_metadata(
        tmp_path,
        Config(),
        request_interval_sec=0.5,
        provider_manager=_FakeProviderManager(fake_get_movie_info),
    )

    assert len(records) == 2
    assert failures == []
    assert summary.api_queries == 2
    assert summary.api_cache_hits == 1
    assert sleeps == [0.5, 0.5]


def test_fetch_metadata_tracks_no_code_and_api_error(tmp_path: Path, monkeypatch) -> None:
    no_code = tmp_path / "plain-title.mp4"
    api_error = tmp_path / "ERR-200.mp4"
    no_code.write_text("x", encoding="utf-8")
    api_error.write_text("x", encoding="utf-8")

    monkeypatch.setattr(
        service,
        "collect_video_files",
        lambda _path: ([no_code, api_error], []),
    )

    def fake_get_movie_info(code: str, cfg: Config) -> MovieInfo:
        del cfg
        raise RuntimeError(f"api failed for {code}")

    records, failures, summary = service.fetch_metadata(
        tmp_path,
        Config(),
        provider_manager=_FakeProviderManager(fake_get_movie_info),
    )

    assert records == []
    assert summary.scanned_files == 2
    assert summary.failed_count == 2
    reasons = [failure.reason for failure in failures]
    assert reasons == ["API_ERROR", "NO_CODE"]


def test_fetch_metadata_keeps_scan_failures(tmp_path: Path, monkeypatch) -> None:
    broken = MetadataFailure(
        file_path=str(tmp_path / "bad.txt"),
        reason="INVALID_INPUT",
        message="bad input",
    )
    monkeypatch.setattr(service, "collect_video_files", lambda _path: ([], [broken]))
    def fake_get_movie_info(_code: str, _cfg: Config) -> MovieInfo:
        return MovieInfo(movie_id="", title="", actors=[])

    records, failures, summary = service.fetch_metadata(
        tmp_path,
        Config(),
        provider_manager=_FakeProviderManager(fake_get_movie_info),
    )

    assert records == []
    assert len(failures) == 1
    assert failures[0].reason == "INVALID_INPUT"
    assert summary.failed_count == 1


def test_fetch_metadata_deduplicates_api_error_by_movie_code(
    tmp_path: Path, monkeypatch
) -> None:
    file_a = tmp_path / "IPSD-048-A.mp4"
    file_b = tmp_path / "IPSD-048-B.mp4"
    file_a.write_text("x", encoding="utf-8")
    file_b.write_text("x", encoding="utf-8")
    monkeypatch.setattr(service, "collect_video_files", lambda _path: ([file_a, file_b], []))

    def fake_get_movie_info(code: str, cfg: Config) -> MovieInfo:
        del cfg
        raise RuntimeError(f"api failed for {code}")

    records, failures, summary = service.fetch_metadata(
        tmp_path,
        Config(),
        provider_manager=_FakeProviderManager(fake_get_movie_info),
    )

    assert records == []
    assert len(failures) == 1
    assert failures[0].reason == "API_ERROR"
    assert failures[0].movie_code == "IPSD-048"
    assert summary.api_queries == 1
    assert summary.api_cache_hits == 1


def test_fetch_metadata_invokes_progress_callbacks(tmp_path: Path, monkeypatch) -> None:
    ok_file = tmp_path / "ABC-123.mp4"
    bad_file = tmp_path / "plain-title.mp4"
    ok_file.write_text("x", encoding="utf-8")
    bad_file.write_text("x", encoding="utf-8")
    monkeypatch.setattr(service, "collect_video_files", lambda _path: ([ok_file, bad_file], []))
    def fake_get_movie_info(code: str, cfg: Config) -> MovieInfo:
        del cfg
        return MovieInfo(
            movie_id=code,
            title="ok",
            actors=["actor"],
            tags=["tagA"],
            cover_url="https://example.com/c.jpg",
        )

    events: list[tuple[str, int, int]] = []

    def on_success(record, processed, total, success_count, failed_count) -> None:
        del record
        events.append(("success", processed, total))
        assert success_count >= 1
        assert failed_count >= 0

    def on_failure(failure, processed, total, success_count, failed_count) -> None:
        del failure
        events.append(("failed", processed, total))
        assert success_count >= 0
        assert failed_count >= 1

    records, failures, summary = service.fetch_metadata(
        tmp_path,
        Config(),
        provider_manager=_FakeProviderManager(fake_get_movie_info),
        on_success=on_success,
        on_failure=on_failure,
    )

    assert len(records) == 1
    assert len(failures) == 1
    assert summary.scanned_files == 2
    assert events == [("success", 1, 2), ("failed", 2, 2)]


def test_fetch_metadata_uses_unknown_amateur_when_actor_missing(
    tmp_path: Path, monkeypatch
) -> None:
    file_a = tmp_path / "ABC-123.mp4"
    file_a.write_text("x", encoding="utf-8")
    monkeypatch.setattr(service, "collect_video_files", lambda _path: ([file_a], []))
    def fake_get_movie_info(code: str, cfg: Config) -> MovieInfo:
        del cfg
        return MovieInfo(
            movie_id=code,
            title="sample",
            actors=[],
            tags=[],
            cover_url="",
        )

    records, failures, summary = service.fetch_metadata(
        tmp_path,
        Config(),
        provider_manager=_FakeProviderManager(fake_get_movie_info),
    )

    assert failures == []
    assert summary.success_count == 1
    assert records[0].actors == ["Unknown Amateur"]
