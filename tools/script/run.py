import sys

from builder.build_runner import run_build
from builder.clang_tidy_runner import run_clang_tidy
from builder.cli import parse_args
from builder.smoke_cli_runner import run_smoke_cli
from builder.test_runner import run_core_tests


def main():
    args = parse_args()

    if args.command == "build":
        return run_build(args)
    if args.command == "clang-tidy":
        return run_clang_tidy(args)
    if args.command == "smoke-cli":
        return run_smoke_cli(args)
    if args.command == "test-core":
        return run_core_tests(args)

    print(f"--- !!! Unknown command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
