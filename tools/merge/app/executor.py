from __future__ import annotations

import os
import shutil
from pathlib import Path

from .models import VideoAction

try:
    from tqdm import tqdm
except ImportError as exc:
    raise RuntimeError("tqdm is required: pip install tqdm") from exc


def copy_with_progress(src_path: Path, dst_path: Path) -> None:
    total_size = src_path.stat().st_size
    chunk_size = 1024 * 1024
    try:
        with open(src_path, "rb") as fsrc, open(dst_path, "wb") as fdst:
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc="  └── 正在复制",
                leave=False,
                ncols=100,
            ) as pbar:
                while True:
                    buf = fsrc.read(chunk_size)
                    if not buf:
                        break
                    fdst.write(buf)
                    pbar.update(len(buf))
        shutil.copystat(src_path, dst_path)
    except KeyboardInterrupt:
        if dst_path.exists():
            dst_path.unlink()
        raise


def execute_action(action: VideoAction) -> tuple[bool, str]:
    if action.kind == "skip_exists":
        return True, f"  └── 跳过 (已存在): {action.source.name}"

    try:
        copy_with_progress(action.source, action.target)
        return True, f"  └── 复制成功: {action.source.name}"
    except Exception as exc:  # noqa: BLE001
        return False, f"  └── 复制失败: {action.source.name} ({exc})"


def delete_source_file(path: Path) -> tuple[bool, str | None]:
    try:
        path.unlink()
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, f"      [警告] 无法删除源视频文件: {path.name} ({exc})"
