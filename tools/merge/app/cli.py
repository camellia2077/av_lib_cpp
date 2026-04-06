from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .service import run_merge


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="同步并在匹配后清理视频文件夹。")
    parser.add_argument("-i", "--input", required=True, help="Input 文件夹路径")
    parser.add_argument("-o", "--output", required=True, help="Output 文件夹路径")
    parser.add_argument("--apply", action="store_true", help="实际执行搬运和删除操作（默认仅预览）")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.is_dir():
        print(f"错误: Input 文件夹不存在或不是目录 -> {input_dir}")
        return
    if not output_dir.is_dir():
        print(f"错误: Output 文件夹不存在或不是目录 -> {output_dir}")
        return

    try:
        run_merge(input_dir=input_dir, output_dir=output_dir, apply=args.apply)
    except KeyboardInterrupt:
        print("\n\n[警告] 检测到 Ctrl + C，已安全终止程序！")
        sys.exit(130)
