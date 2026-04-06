from __future__ import annotations

from collections.abc import Callable
import time
from pathlib import Path

from ..extract_codes.service import load_entries_from_json
from ..move_by_actor.app.config import Config
from ..providers.base import ProviderResult
from ..providers.manager import (
    ProviderChainError,
    ProviderManager,
    build_default_provider_manager,
)
from .models import FetchSummary, MetadataFailure, MetadataRecord
from .parser import extract_standard_movie_code
from .scanner import collect_video_files

SuccessCallback = Callable[[MetadataRecord, int, int, int, int], None]
FailureCallback = Callable[[MetadataFailure, int, int, int, int], None]
ScanStartCallback = Callable[[str], None]
ScanDoneCallback = Callable[[int, int], None]
TryCodeCallback = Callable[[str, int, int, str, bool], None]
UNKNOWN_AMATEUR_NAME = "Unknown Amateur"


def _candidate_stem(raw_value: str) -> str:
    raw = raw_value.strip()
    if "\\" in raw or "/" in raw:
        return Path(raw).stem
    if "." in raw:
        return Path(raw).stem
    return raw


def _fetch_from_sources(
    *,
    sources: list[tuple[str, str]],
    cfg: Config,
    initial_failures: list[MetadataFailure],
    request_interval_sec: float,
    provider_manager: ProviderManager,
    on_success: SuccessCallback | None,
    on_failure: FailureCallback | None,
    on_try_code: TryCodeCallback | None,
) -> tuple[list[MetadataRecord], list[MetadataFailure], FetchSummary]:
    failures = list(initial_failures)
    records: list[MetadataRecord] = []
    code_cache: dict[str, ProviderResult | Exception] = {}
    api_queries = 0
    api_cache_hits = 0
    emitted_success_codes: set[str] = set()
    emitted_api_error_codes: set[str] = set()
    total = len(sources)
    processed = 0
    success_count = 0
    failed_count = len(failures)

    if on_failure:
        for failure in failures:
            on_failure(failure, processed, total, success_count, failed_count)

    for source_path, raw_value in sources:
        processed += 1
        code = extract_standard_movie_code(_candidate_stem(raw_value))
        if not code:
            failure = MetadataFailure(
                file_path=source_path,
                reason="NO_CODE",
                message="Cannot parse a standard movie code from input value.",
            )
            failures.append(failure)
            failed_count += 1
            if on_failure:
                on_failure(failure, processed, total, success_count, failed_count)
            continue

        cached = code_cache.get(code)
        if on_try_code:
            on_try_code(
                code,
                processed,
                total,
                source_path,
                cached is not None,
            )
        if cached is None:
            api_queries += 1
            try:
                cached = provider_manager.fetch_movie_info(code, cfg=cfg)
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                cached = exc
            finally:
                # Keep outbound behavior human-like and predictable:
                # one request at a time, with optional fixed interval.
                if request_interval_sec > 0:
                    time.sleep(request_interval_sec)
            code_cache[code] = cached
        else:
            api_cache_hits += 1

        if isinstance(cached, Exception):
            if code in emitted_api_error_codes:
                continue
            reason = "API_ERROR"
            attempts: list[dict[str, str]] = []
            if isinstance(cached, ProviderChainError):
                if cached.kind == "not_found":
                    reason = "NOT_FOUND"
                attempts = [
                    {
                        "provider": item.provider_name,
                        "status": item.status,
                        "message": item.message,
                    }
                    for item in cached.attempts
                ]
            failure = MetadataFailure(
                file_path=source_path,
                movie_code=code,
                reason=reason,  # type: ignore[arg-type]
                message=str(cached),
                provider_attempts=attempts,
            )
            emitted_api_error_codes.add(code)
            failures.append(failure)
            failed_count += 1
            if on_failure:
                on_failure(failure, processed, total, success_count, failed_count)
            continue

        # Multiple split files may resolve to the same normalized movie code
        # (e.g. IPSD-048-A/B). Emit one metadata row per canonical movie code.
        if code in emitted_success_codes:
            continue
        # Some amateur titles do not expose actor names in upstream metadata.
        # Keep output schema stable by assigning a neutral placeholder name.
        actors = cached.movie.actors if cached.movie.actors else [UNKNOWN_AMATEUR_NAME]
        record = MetadataRecord(
            file_path=source_path,
            movie_code=code,
            title=cached.movie.title,
            actors=actors,
            tags=cached.movie.tags or [],
            cover_url=cached.movie.cover_url,
            date=cached.movie.date,
            studio=cached.movie.studio,
            series=cached.movie.series,
            provider=cached.provider_name,
            provider_attempts=[
                {
                    "provider": item.provider_name,
                    "status": item.status,
                    "message": item.message,
                }
                for item in cached.attempts
            ],
        )
        emitted_success_codes.add(code)
        records.append(record)
        success_count += 1
        if on_success:
            on_success(record, processed, total, success_count, failed_count)

    records.sort(key=lambda item: item.file_path.lower())
    failures.sort(key=lambda item: item.file_path.lower())
    summary = FetchSummary(
        scanned_files=total,
        success_count=success_count,
        failed_count=failed_count,
        api_queries=api_queries,
        api_cache_hits=api_cache_hits,
    )
    return records, failures, summary


def fetch_metadata(
    input_path: Path,
    cfg: Config,
    request_interval_sec: float = 0.0,
    provider_manager: ProviderManager | None = None,
    on_success: SuccessCallback | None = None,
    on_failure: FailureCallback | None = None,
    on_scan_start: ScanStartCallback | None = None,
    on_scan_done: ScanDoneCallback | None = None,
    on_try_code: TryCodeCallback | None = None,
) -> tuple[list[MetadataRecord], list[MetadataFailure], FetchSummary]:
    provider_manager = provider_manager or build_default_provider_manager()
    if on_scan_start:
        on_scan_start(str(input_path))
    video_files, failures = collect_video_files(input_path)
    if on_scan_done:
        on_scan_done(len(video_files), len(failures))
    sources = [(str(path), path.stem) for path in video_files]
    return _fetch_from_sources(
        sources=sources,
        cfg=cfg,
        initial_failures=failures,
        request_interval_sec=request_interval_sec,
        provider_manager=provider_manager,
        on_success=on_success,
        on_failure=on_failure,
        on_try_code=on_try_code,
    )


def fetch_metadata_from_codes_json(
    codes_json_path: Path,
    cfg: Config,
    request_interval_sec: float = 0.0,
    provider_manager: ProviderManager | None = None,
    on_success: SuccessCallback | None = None,
    on_failure: FailureCallback | None = None,
    on_scan_start: ScanStartCallback | None = None,
    on_scan_done: ScanDoneCallback | None = None,
    on_try_code: TryCodeCallback | None = None,
) -> tuple[list[MetadataRecord], list[MetadataFailure], FetchSummary]:
    provider_manager = provider_manager or build_default_provider_manager()
    if on_scan_start:
        on_scan_start(str(codes_json_path))
    entries, parse_errors = load_entries_from_json(codes_json_path)
    failures = [
        MetadataFailure(
            file_path=str(codes_json_path),
            reason="INVALID_INPUT",
            message=message,
        )
        for message in parse_errors
    ]
    if on_scan_done:
        on_scan_done(len(entries), len(failures))
    sources = [(entry.source, entry.raw_value) for entry in entries]
    return _fetch_from_sources(
        sources=sources,
        cfg=cfg,
        initial_failures=failures,
        request_interval_sec=request_interval_sec,
        provider_manager=provider_manager,
        on_success=on_success,
        on_failure=on_failure,
        on_try_code=on_try_code,
    )
