from __future__ import annotations

import argparse
from pathlib import Path

from .api_runtime import ensure_api_ready
from .config import ApiRuntimeOptions, Config, RuntimeConfigFile, default_runtime_config_path
from .runtime_config import load_runtime_config
from .service import move_videos_by_actor

DEFAULT_CONFIG = Config()
DEFAULT_RUNTIME_CONFIG = RuntimeConfigFile(api=ApiRuntimeOptions())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan videos, query actor by movie code via API, and move files into actor folders."
        )
    )
    parser.add_argument(
        "--input",
        required=False,
        help="Input directory containing videos",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output root directory for actor folders (default: input directory)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply move operations (default: preview only)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan input directory recursively",
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
        "--no-env-proxy",
        action="store_true",
        help="Disable using HTTP_PROXY/HTTPS_PROXY from environment",
    )
    parser.add_argument(
        "--runtime-config",
        default=str(default_runtime_config_path()),
        help="Path to runtime TOML config (default: tools/move_by_actor/runtime.toml)",
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
        help="Only ensure API is running, then exit without scanning/moving",
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
        # Start-only mode should be able to auto-start API without requiring
        # scanning arguments.
        runtime_options.auto_start = True

    input_dir: Path | None = None
    dest_root: Path | None = None
    if not args.start_api_only:
        if not args.input:
            raise SystemExit("--input is required unless --start-api-only is used.")
        input_dir = Path(args.input).expanduser().resolve()
        if not input_dir.exists() or not input_dir.is_dir():
            raise SystemExit(f"Invalid directory: {input_dir}")
        dest_root = (
            Path(args.output).expanduser().resolve() if args.output else input_dir
        )

    mode = "APPLY" if args.apply else "PREVIEW"
    if input_dir is not None:
        print(f"[{mode}] input={input_dir}")
        print(f"[{mode}] dest_root={dest_root}")
    print(f"[{mode}] api_base={cfg.api_base}, timeout={cfg.timeout}s")
    print(
        f"[{mode}] api_healthcheck={runtime_options.healthcheck_url}, "
        f"auto_start_api={runtime_options.auto_start}"
    )

    started_api_process = None
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
            print("[INFO] Start-only mode completed. No scan/move executed.")
            return

        scanned_count, moved_count, interrupted = move_videos_by_actor(
            input_dir=input_dir,  # type: ignore[arg-type]
            dest_root=dest_root,  # type: ignore[arg-type]
            apply_changes=args.apply,
            recursive=args.recursive,
            cfg=cfg,
        )
        print(
            f"[SUMMARY] scanned={scanned_count}, movable={moved_count}, applied={args.apply}"
        )
        if not args.apply:
            print("[PREVIEW] Dry-run only. Add --apply to perform actual moves.")
        if interrupted:
            print("[INTERRUPTED] Ctrl+C received, task stopped safely.")
            raise SystemExit(130)
    finally:
        if (
            started_api_process is not None
            and runtime_options.stop_on_exit
            and not args.start_api_only
        ):
            started_api_process.terminate()
            print("[INFO] Auto-started API process terminated.")
