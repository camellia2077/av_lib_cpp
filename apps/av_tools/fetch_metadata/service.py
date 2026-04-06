from __future__ import annotations

from collections.abc import Callable
import time
from pathlib import Path

from ..move_by_actor.app.config import Config
from ..move_by_actor.app.models import MovieInfo
from ..providers.manager import ProviderManager, build_default_provider_manager
from .models import FetchSummary, MetadataFailure, MetadataRecord
from .parser import extract_standard_movie_code
from .scanner import collect_video_files

SuccessCallback = Callable[[MetadataRecord, int, int, int, int], None]
FailureCallback = Callable[[MetadataFailure, int, int, int, int], None]
UNKNOWN_AMATEUR_NAME = "Unknown Amateur"


def fetch_metadata(
    input_path: Path,
    cfg: Config,
    request_interval_sec: float = 0.0,
    provider_manager: ProviderManager | None = None,
    on_success: SuccessCallback | None = None,
    on_failure: FailureCallback | None = None,
) -> tuple[list[MetadataRecord], list[MetadataFailure], FetchSummary]:
    provider_manager = provider_manager or build_default_provider_manager()
    video_files, failures = collect_video_files(input_path)
    records: list[MetadataRecord] = []
    code_cache: dict[str, MovieInfo | Exception] = {}
    api_queries = 0
    api_cache_hits = 0
    emitted_success_codes: set[str] = set()
    emitted_api_error_codes: set[str] = set()
    total = len(video_files)
    processed = 0
    success_count = 0
    failed_count = len(failures)

    if on_failure:
        for failure in failures:
            on_failure(failure, processed, total, success_count, failed_count)

    for file_path in video_files:
        processed += 1
        code = extract_standard_movie_code(file_path.stem)
        if not code:
            failure = MetadataFailure(
                file_path=str(file_path),
                reason="NO_CODE",
                message="Cannot parse a standard movie code from file name.",
            )
            failures.append(failure)
            failed_count += 1
            if on_failure:
                on_failure(failure, processed, total, success_count, failed_count)
            continue

        cached = code_cache.get(code)
        if cached is None:
            api_queries += 1
            try:
                cached = provider_manager.fetch_movie_info(code, cfg=cfg).movie
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
            failure = MetadataFailure(
                file_path=str(file_path),
                movie_code=code,
                reason="API_ERROR",
                message=str(cached),
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
        actors = cached.actors if cached.actors else [UNKNOWN_AMATEUR_NAME]
        record = MetadataRecord(
            file_path=str(file_path),
            movie_code=code,
            title=cached.title,
            actors=actors,
            tags=cached.tags or [],
            cover_url=cached.cover_url,
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
