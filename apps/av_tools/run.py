from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from . import __version__


def _dispatch(command: str, forwarded_args: Sequence[str]) -> None:
    if command == "index-formatter":
        from .index_formatter.run import main as index_formatter_main

        sys.argv = [f"{sys.argv[0]} {command}", *forwarded_args]
        index_formatter_main()
        return

    if command == "move-by-actor":
        from .move_by_actor.app.cli import main as move_by_actor_main

        sys.argv = [f"{sys.argv[0]} {command}", *forwarded_args]
        move_by_actor_main()
        return

    if command == "fetch-metadata":
        from .fetch_metadata.cli import main as fetch_metadata_main

        sys.argv = [f"{sys.argv[0]} {command}", *forwarded_args]
        fetch_metadata_main()
        return
    
    if command == "extract-codes":
        from .extract_codes.cli import main as extract_codes_main

        sys.argv = [f"{sys.argv[0]} {command}", *forwarded_args]
        extract_codes_main()
        return

    raise SystemExit(f"Unknown subcommand: {command}")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Unified AV tools entrypoint. Use subcommands for specific workflows."
        )
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "command",
        choices=["index-formatter", "move-by-actor", "fetch-metadata", "extract-codes"],
        help="Subcommand to run",
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments passed through to the selected subcommand",
    )
    parsed = parser.parse_args(argv)

    forwarded_args = list(parsed.args)
    if forwarded_args and forwarded_args[0] == "--":
        forwarded_args = forwarded_args[1:]
    _dispatch(parsed.command, forwarded_args)


if __name__ == "__main__":
    main()
