import argparse
from pathlib import Path

from .core.renamer import process


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recursively sanitize video filenames: keep only A-Z a-z 0-9 and '-'"
    )
    parser.add_argument("input_dir", help="Directory to scan recursively")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply rename changes (default is preview only)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-file rename output and only perform processing",
    )
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="Color mode for preview output (default: auto)",
    )
    args = parser.parse_args()

    root = Path(args.input_dir).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Invalid directory: {root}")

    process(root, apply_changes=args.apply, quiet=args.quiet, color=args.color)


if __name__ == "__main__":
    main()

