from __future__ import annotations

import argparse
from collections import deque
from dataclasses import replace
import os
from pathlib import Path
import signal

from tqdm import tqdm

from ..move_by_actor.app.api_runtime import ensure_api_ready
from ..move_by_actor.app.config import (
    ApiRuntimeOptions,
    Config,
    RuntimeConfigFile,
    default_runtime_config_path,
)
from ..move_by_actor.app.runtime_config import load_runtime_config
from ..providers.manager import build_provider_manager_from_runtime
from ..providers.runtime_options import (
    BrowserFallbackMode,
    ProvidersRuntimeOptions,
    load_providers_runtime_options,
)
from .service import fetch_metadata, fetch_metadata_from_codes_json
from .writers import StreamingReportWriter, write_json_reports

DEFAULT_CONFIG = Config()
DEFAULT_RUNTIME_CONFIG = RuntimeConfigFile(api=ApiRuntimeOptions())
DEFAULT_PROVIDERS_RUNTIME = ProvidersRuntimeOptions()
DEFAULT_OUTPUT_DIR = Path("out/av_tools/fetch_metadata")
DOWNLOAD_MODE_OVERRIDES: dict[str, dict[str, object]] = {
    "api-only": {
        "browser_mode": "off",
        "enabled_providers": ["javbus_api"],
    },
    "http": {
        "browser_mode": "off",
    },
    "browser-on-error": {
        "browser_mode": "on_error",
    },
    "browser-always": {
        "browser_mode": "always",
    },
    "browser-only": {
        "browser_mode": "off",
        "enabled_providers": ["javbus_browser"],
    },
}
SUPPORTED_PROVIDER_NAMES = {"javdb", "javbus_api", "r18", "javbus_browser"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Recursively scan videos, parse movie code, query API metadata, and "
            "export JSON/CSV reports."
        )
    )
    parser.add_argument(
        "--input",
        required=False,
        help="Input path (directory for recursive scan, or a single video file)",
    )
    parser.add_argument(
        "--codes-json",
        required=False,
        help="Input JSON path containing code-like values (skip file scanning)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for reports (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--api-base",
        default=DEFAULT_CONFIG.api_base,
        help=f"API base URL (default: {DEFAULT_CONFIG.api_base})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help=(
            "API timeout in seconds for javbus_api (default: "
            f"{DEFAULT_CONFIG.timeout})"
        ),
    )
    parser.add_argument(
        "--provider-timeout",
        type=int,
        default=None,
        help=(
            "Provider network timeout in seconds (CLI priority over runtime "
            "providers.network.timeout_sec)"
        ),
    )
    parser.add_argument(
        "--request-interval",
        type=float,
        default=None,
        help=(
            "Sleep seconds between outbound API queries for new movie codes "
            "(default: from runtime providers.network.request_interval_sec, set 0 to disable)"
        ),
    )
    parser.add_argument(
        "--providers",
        default=None,
        help=(
            "Provider order override, comma-separated (CLI priority over runtime.toml), "
            "e.g. javdb,r18"
        ),
    )
    parser.add_argument(
        "--download-mode",
        choices=list(DOWNLOAD_MODE_OVERRIDES.keys()),
        default=None,
        help=(
            "Download/fetch mode override (CLI priority over runtime.toml): "
            "api-only | http | browser-on-error | browser-always | browser-only"
        ),
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Force Playwright to run with a visible browser window (headless=false)",
    )
    parser.add_argument(
        "--no-env-proxy",
        action="store_true",
        help="Disable using HTTP_PROXY/HTTPS_PROXY from environment",
    )
    parser.add_argument(
        "--runtime-config",
        default=str(default_runtime_config_path()),
        help=(
            "Path to runtime TOML config "
            "(default: apps/av_tools/move_by_actor/runtime.toml)"
        ),
    )
    parser.add_argument(
        "--auto-start-api",
        action="store_true",
        help="Force auto start API when healthcheck fails",
    )
    parser.add_argument(
        "--stop-api-on-exit",
        action="store_true",
        help="If this run starts API automatically, stop it before exit",
    )
    parser.add_argument(
        "--start-api-only",
        action="store_true",
        help="Only ensure API is running, then exit without scanning/fetching",
    )
    return parser.parse_args()


def _parse_providers_override(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise SystemExit("--providers cannot be empty.")
    invalid = [name for name in values if name not in SUPPORTED_PROVIDER_NAMES]
    if invalid:
        raise SystemExit(
            f"Unsupported provider(s): {','.join(invalid)}. "
            f"Supported: {','.join(sorted(SUPPORTED_PROVIDER_NAMES))}"
        )
    return values


def _force_enable_selected_providers(
    options: ProvidersRuntimeOptions,
    selected: list[str],
) -> ProvidersRuntimeOptions:
    updated = options
    if "javdb" in selected:
        updated = replace(updated, javdb=replace(updated.javdb, enabled=True))
    if "javbus_api" in selected:
        updated = replace(
            updated,
            javbus_api=replace(updated.javbus_api, enabled=True),
        )
    if "r18" in selected:
        updated = replace(updated, r18=replace(updated.r18, enabled=True))
    if "javbus_browser" in selected:
        updated = replace(
            updated,
            javbus_browser=replace(updated.javbus_browser, enabled=True),
        )
    return updated


def main() -> None:
    args = parse_args()
    previous_sigint_handler = signal.getsignal(signal.SIGINT)
    sigint_state = {"count": 0}

    def _sigint_handler(_signum, _frame) -> None:
        sigint_state["count"] += 1
        if sigint_state["count"] >= 2:
            # Second Ctrl+C: force stop in case third-party libs keep blocking.
            os._exit(130)
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _sigint_handler)
    if hasattr(signal, "siginterrupt"):
        try:
            signal.siginterrupt(signal.SIGINT, True)
        except Exception:
            pass

    runtime_config_path = Path(args.runtime_config).expanduser().resolve()
    provider_runtime = load_providers_runtime_options(runtime_config_path)
    if args.download_mode is not None:
        override = DOWNLOAD_MODE_OVERRIDES[args.download_mode]
        browser_mode = override["browser_mode"]
        enabled_providers = list(override.get("enabled_providers", provider_runtime.enabled))
        provider_runtime = replace(
            provider_runtime,
            enabled=enabled_providers,  # type: ignore[arg-type]
            browser_fallback=replace(
                provider_runtime.browser_fallback,
                mode=browser_mode,  # type: ignore[arg-type]
            ),
        )
        provider_runtime = _force_enable_selected_providers(provider_runtime, enabled_providers)
    if args.providers is not None:
        selected_providers = _parse_providers_override(args.providers)
        provider_runtime = replace(
            provider_runtime,
            enabled=selected_providers,
        )
        provider_runtime = _force_enable_selected_providers(
            provider_runtime,
            selected_providers,
        )
    if args.provider_timeout is not None:
        provider_runtime = replace(
            provider_runtime,
            network=replace(
                provider_runtime.network,
                timeout_sec=max(1, int(args.provider_timeout)),
            ),
        )
    if args.show_browser:
        provider_runtime = replace(
            provider_runtime,
            javbus_browser=replace(
                provider_runtime.javbus_browser,
                headless=False,
            ),
            browser_fallback=replace(
                provider_runtime.browser_fallback,
                headless=False,
            ),
        )
    effective_timeout = (
        int(args.timeout)
        if args.timeout is not None
        else DEFAULT_CONFIG.timeout
    )
    effective_interval = (
        float(args.request_interval)
        if args.request_interval is not None
        else provider_runtime.network.request_interval_sec
    )

    cfg = Config(
        api_base=args.api_base,
        timeout=effective_timeout,
        use_env_proxy=not args.no_env_proxy,
    )
    runtime_config = load_runtime_config(
        path=runtime_config_path,
        defaults=DEFAULT_RUNTIME_CONFIG,
    )
    runtime_options = runtime_config.api
    if args.auto_start_api:
        runtime_options.auto_start = True
    if args.stop_api_on_exit:
        runtime_options.stop_on_exit = True
    if args.start_api_only:
        runtime_options.auto_start = True

    input_path: Path | None = None
    codes_json_path: Path | None = None
    if not args.start_api_only:
        if bool(args.input) == bool(args.codes_json):
            raise SystemExit("Exactly one of --input or --codes-json is required unless --start-api-only is used.")
        if args.input:
            input_path = Path(args.input).expanduser().resolve()
            if not input_path.exists():
                raise SystemExit(f"Invalid path: {input_path}")
        if args.codes_json:
            codes_json_path = Path(args.codes_json).expanduser().resolve()
            if not codes_json_path.exists() or not codes_json_path.is_file():
                raise SystemExit(f"Invalid JSON path: {codes_json_path}")

    output_dir = Path(args.output_dir).expanduser().resolve()

    if input_path is not None:
        print(f"[RUN] input={input_path}")
    if codes_json_path is not None:
        print(f"[RUN] codes_json={codes_json_path}")
    print(f"[RUN] output_dir={output_dir}")
    print(
        f"[RUN] api_base={cfg.api_base}, api_timeout={cfg.timeout}s, "
        f"provider_timeout={provider_runtime.network.timeout_sec}s"
    )
    print(f"[RUN] concurrency=1, request_interval={effective_interval}s")
    print(f"[RUN] providers={provider_runtime.enabled}")
    print(f"[RUN] browser_fallback_mode={provider_runtime.browser_fallback.mode}")
    print(f"[RUN] javbus_browser_headless={provider_runtime.javbus_browser.headless}")
    print(f"[RUN] browser_headless={provider_runtime.browser_fallback.headless}")
    print(
        f"[RUN] api_healthcheck={runtime_options.healthcheck_url}, "
        f"auto_start_api={runtime_options.auto_start}"
    )

    started_api_process = None
    stream_writer: StreamingReportWriter | None = None
    progress_bar: tqdm | None = None
    last_processed = 0
    recent_success_codes: deque[str] = deque(maxlen=3)
    last_total = 0
    last_success = 0
    last_failed = 0
    active_try = "-"
    try:
        try:
            started_api_process = ensure_api_ready(runtime_options)
        except Exception as exc:
            raise SystemExit(f"[ERROR] {exc}") from exc
        if started_api_process is not None:
            print("[INFO] API auto-started and is healthy.")
        else:
            print("[INFO] API is already healthy.")

        if args.start_api_only:
            print("[INFO] Start-only mode completed. No scan/fetch executed.")
            return

        stream_writer = StreamingReportWriter(output_dir=output_dir)
        stream_paths = stream_writer.output_paths()
        provider_manager = build_provider_manager_from_runtime(
            provider_runtime,
            use_env_proxy=cfg.use_env_proxy,
        )
        print(
            "[STREAM] "
            f"result_csv={stream_paths['result_csv']}, "
            f"failed_csv={stream_paths['failed_csv']}"
        )

        def _update_progress(
            processed,
            total,
            success_count,
            failed_count,
            *,
            force_refresh: bool = False,
        ) -> None:
            nonlocal progress_bar
            nonlocal last_processed
            nonlocal last_total
            nonlocal last_success
            nonlocal last_failed
            if total <= 0:
                return
            last_total = total
            last_success = success_count
            last_failed = failed_count
            if progress_bar is None:
                progress_bar = tqdm(
                    total=total,
                    desc="fetch-metadata",
                    unit="file",
                    dynamic_ncols=True,
                )
            delta = max(0, processed - last_processed)
            if delta:
                progress_bar.update(delta)
                last_processed = processed
            padded = ["-", "-", "-"]
            recent = list(recent_success_codes)
            if recent:
                padded[-len(recent) :] = recent
            progress_bar.set_postfix(
                {
                    "success": success_count,
                    "failed": failed_count,
                    "code1": padded[0],
                    "code2": padded[1],
                    "code3": padded[2],
                    "try": active_try,
                },
                refresh=force_refresh,
            )

        def _on_success(record, processed, total, success_count, failed_count) -> None:
            if stream_writer is not None:
                stream_writer.append_success(record)
            recent_success_codes.append(record.movie_code)
            _update_progress(processed, total, success_count, failed_count)

        def _on_failure(failure, processed, total, success_count, failed_count) -> None:
            if stream_writer is not None:
                stream_writer.append_failure(failure)
            _update_progress(processed, total, success_count, failed_count)

        def _on_scan_start(input_label: str) -> None:
            print(f"[SCAN] start source={input_label}")

        def _on_scan_done(total_sources: int, initial_failures: int) -> None:
            print(
                "[SCAN] done "
                f"total_sources={total_sources}, initial_failures={initial_failures}"
            )
            _update_progress(
                0,
                total_sources,
                0,
                initial_failures,
                force_refresh=True,
            )

        def _on_try_code(code, processed, total, source_path, is_cache_hit) -> None:
            nonlocal active_try
            source_name = Path(source_path).name
            if len(source_name) > 28:
                source_name = f"...{source_name[-25:]}"
            cache_suffix = " cache" if is_cache_hit else ""
            active_try = f"{code}{cache_suffix}@{source_name}"
            _update_progress(
                last_processed,
                total or last_total,
                last_success,
                last_failed,
                force_refresh=True,
            )

        try:
            if codes_json_path is not None:
                records, failures, summary = fetch_metadata_from_codes_json(
                    codes_json_path=codes_json_path,
                    cfg=cfg,
                    request_interval_sec=max(0.0, effective_interval),
                    provider_manager=provider_manager,
                    on_success=_on_success,
                    on_failure=_on_failure,
                    on_scan_start=_on_scan_start,
                    on_scan_done=_on_scan_done,
                    on_try_code=_on_try_code,
                )
            else:
                records, failures, summary = fetch_metadata(
                    input_path=input_path,  # type: ignore[arg-type]
                    cfg=cfg,
                    request_interval_sec=max(0.0, effective_interval),
                    provider_manager=provider_manager,
                    on_success=_on_success,
                    on_failure=_on_failure,
                    on_scan_start=_on_scan_start,
                    on_scan_done=_on_scan_done,
                    on_try_code=_on_try_code,
                )
        except KeyboardInterrupt as exc:
            print("[INTERRUPTED] Ctrl+C received, task stopped safely.")
            raise SystemExit(130) from exc

        if stream_writer is not None:
            stream_writer.close()

        report_input = codes_json_path if codes_json_path is not None else input_path
        json_outputs = write_json_reports(
            output_dir=output_dir,
            input_path=report_input,  # type: ignore[arg-type]
            records=records,
            failures=failures,
            summary=summary,
        )
        outputs = {
            **stream_paths,
            "result_json": json_outputs["result_json"],
            "failed_json": json_outputs["failed_json"],
        }
        print(
            "[SUMMARY] "
            f"scanned={summary.scanned_files}, "
            f"success={summary.success_count}, "
            f"failed={summary.failed_count}, "
            f"api_queries={summary.api_queries}, "
            f"api_cache_hits={summary.api_cache_hits}"
        )
        print(
            "[OUTPUT] "
            f"result_json={outputs['result_json']}, "
            f"failed_json={outputs['failed_json']}, "
            f"result_csv={outputs['result_csv']}, "
            f"failed_csv={outputs['failed_csv']}"
        )
    finally:
        signal.signal(signal.SIGINT, previous_sigint_handler)
        if progress_bar is not None:
            progress_bar.close()
        if stream_writer is not None:
            stream_writer.close()
        if started_api_process is not None and runtime_options.stop_on_exit:
            started_api_process.terminate()
            print("[INFO] Auto-started API process terminated.")
