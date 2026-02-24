import sys

from builder.build_runner import run_build
from builder.clang_tidy_runner import run_clang_tidy
from builder.cli import parse_args


def main():
    args = parse_args()
    if args.run_clang_tidy:
        sys.exit(run_clang_tidy(args))
    if args.files:
        print(f"--- !!! Unexpected positional args: {' '.join(args.files)}", file=sys.stderr)
        sys.exit(2)
    sys.exit(run_build(args))


if __name__ == "__main__":
    main()
