from __future__ import annotations

import shutil
from pathlib import Path

from .api_client import get_movie_info
from .config import Config
from .file_ops import sanitize_actor_dir_name, unique_target_path
from .models import MovieInfo
from .scanner import scan_items_for_move

ANSI_GREEN = "\x1b[92m"
ANSI_RESET = "\x1b[0m"


def _format_move_line(text: str, apply_changes: bool) -> str:
    # Keep preview output plain; highlight only real move operations.
    if not apply_changes:
        return text
    return f"{ANSI_GREEN}{text}{ANSI_RESET}"


def move_videos_by_actor(
    input_dir: Path,
    dest_root: Path,
    apply_changes: bool,
    recursive: bool,
    cfg: Config,
) -> tuple[int, int, bool]:
    scanned = 0
    moved = 0
    code_cache: dict[str, MovieInfo | Exception] = {}

    items = scan_items_for_move(input_dir, recursive=recursive)
    try:
        for item in items:
            scanned += 1
            code = item.code_hint
            source_path = item.path
            if not code:
                print(f"[SKIP][NO-CODE] {source_path.name}")
                continue

            cached = code_cache.get(code)
            if cached is None:
                # Cache by movie code to avoid repeated API calls when multiple
                # files/folders map to the same normalized code.
                try:
                    cached = get_movie_info(code, cfg=cfg)
                except Exception as exc:
                    cached = exc
                code_cache[code] = cached

            if isinstance(cached, Exception):
                print(f"[SKIP][API-ERROR] {source_path.name} ({code}) -> {cached}")
                continue

            actors = cached.actors
            # Safety rule: move only when actor mapping is unambiguous.
            if len(actors) != 1:
                print(
                    f"[SKIP][ACTOR-COUNT={len(actors)}] {source_path.name} ({code}) -> {actors}"
                )
                continue

            actor_dir = sanitize_actor_dir_name(actors[0])
            target_dir = dest_root / actor_dir
            target = target_dir / source_path.name
            if target.exists() and target.resolve() != source_path.resolve():
                target = unique_target_path(target)

            unit = "DIR" if item.is_dir else "FILE"
            line = f"[MOVE][{unit}] {source_path} -> {target}"
            print(_format_move_line(line, apply_changes=apply_changes))
            if apply_changes:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(target))
            moved += 1
    except KeyboardInterrupt:
        return scanned, moved, True

    return scanned, moved, False
