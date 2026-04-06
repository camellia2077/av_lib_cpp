import pathlib

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent.parent
SOURCE_DIR = SCRIPT_DIR.parent.parent
OUT_DIR = SOURCE_DIR / "out"
BUILD_ROOT_DIR = OUT_DIR / "build"
