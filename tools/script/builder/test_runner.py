from pathlib import Path

from .cmake_utils import cmake_define, run_command
from .paths import SOURCE_DIR


def run_core_tests(args):
    build_dir = Path(args.build_dir)
    if not build_dir.is_absolute():
        build_dir = SOURCE_DIR / build_dir
    build_dir.mkdir(parents=True, exist_ok=True)

    run_command(
        [
            "cmake",
            "-S",
            str(SOURCE_DIR),
            "-B",
            str(build_dir),
            cmake_define("CMAKE_BUILD_TYPE", args.config),
            cmake_define("BUILD_TESTING", "ON"),
            cmake_define("AVLIB_STATIC_LINK", "ON"),
        ]
    )
    run_command(["cmake", "--build", str(build_dir), "--config", args.config, "--target", "avlib_core_tests"])
    run_command(["ctest", "--test-dir", str(build_dir), "--output-on-failure", "-R", "avlib_core_tests"])
    return 0
