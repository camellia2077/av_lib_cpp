from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from tqdm import tqdm

from ..move_by_actor.app.api_runtime import ensure_api_ready
from ..move_by_actor.app.config import (
    ApiRuntimeOptions,
    Config,
    RuntimeConfigFile,
    default_runtime_config_path,
)
from ..move_by_actor.app.runtime_config import load_runtime_config
from .service import fetch_metadata
from .writers import StreamingReportWriter, write_json_reports

DEFAULT_CONFIG = Config()
DEFAULT_RUNTIME_CONFIG = RuntimeConfigFile(api=ApiRuntimeOptions())
DEFAULT_OUTPUT_DIR = Path("out/av_tools/fetch_metadata")


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
        default=DEFAULT_CONFIG.timeout,
        help=f"HTTP timeout in seconds (default: {DEFAULT_CONFIG.timeout})",
    )
    parser.add_argument(
        "--request-interval",
        type=float,
        default=1.0,
        help=(
            "Sleep seconds between outbound API queries for new movie codes "
            "(default: 1.0, set 0 to disable)"
        ),
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


def main() -> None:
    args = parse_args()
    cfg = Config(
        api_base=args.api_base,
        timeout=args.timeout,
        use_env_proxy=not args.no_env_proxy,
    )
    runtime_config_path = Path(args.runtime_config).expanduser().resolve()
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
    if not args.start_api_only:
        if not args.input:
            raise SystemExit("--input is required unless --start-api-only is used.")
        input_path = Path(args.input).expanduser().resolve()
        if not input_path.exists():
            raise SystemExit(f"Invalid path: {input_path}")
    output_dir = Path(args.output_dir).expanduser().resolve()

    if input_path is not None:
        print(f"[RUN] input={input_path}")
    print(f"[RUN] output_dir={output_dir}")
    print(f"[RUN] api_base={cfg.api_base}, timeout={cfg.timeout}s")
    print(f"[RUN] concurrency=1, request_interval={args.request_interval}s")
    print(
        f"[RUN] api_healthcheck={runtime_options.healthcheck_url}, "
        f"auto_start_api={runtime_options.auto_start}"
    )

    started_api_process = None
    stream_writer: StreamingReportWriter | None = None
    progress_bar: tqdm | None = None
    last_processed = 0
    recent_success_codes: deque[str] = deque(maxlen=3)
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
        print(
            "[STREAM] "
            f"result_csv={stream_paths['result_csv']}, "
            f"failed_csv={stream_paths['failed_csv']}"
        )

        def _update_progress(processed, total, success_count, failed_count) -> None:
            nonlocal progress_bar
            nonlocal last_processed
            if total <= 0:
                return
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
                },
                refresh=False,
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

        try:
            records, failures, summary = fetch_metadata(
                input_path=input_path,  # type: ignore[arg-type]
                cfg=cfg,
                request_interval_sec=max(0.0, args.request_interval),
                on_success=_on_success,
                on_failure=_on_failure,
            )
        except KeyboardInterrupt as exc:
            print("[INTERRUPTED] Ctrl+C received, task stopped safely.")
            raise SystemExit(130) from exc

        if stream_writer is not None:
            stream_writer.close()

        json_outputs = write_json_reports(
            output_dir=output_dir,
            input_path=input_path,  # type: ignore[arg-type]
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
        if progress_bar is not None:
            progress_bar.close()
        if stream_writer is not None:
            stream_writer.close()
        if started_api_process is not None and runtime_options.stop_on_exit:
            started_api_process.terminate()
            print("[INFO] Auto-started API process terminated.")
