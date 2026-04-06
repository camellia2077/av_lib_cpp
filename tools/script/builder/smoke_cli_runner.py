import subprocess
from pathlib import Path

from .paths import OUT_DIR, SOURCE_DIR


def _resolve_repo_path(path_like):
    candidate = Path(path_like)
    if candidate.exists():
        return candidate.resolve()
    candidate = (SOURCE_DIR / path_like).resolve()
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Path not found: {path_like}")


def run_smoke_cli(args):
    try:
        exe_full_path = _resolve_repo_path(args.exe_path)
    except FileNotFoundError as exc:
        print(f"--- !!! {exc}")
        return 2

    smoke_dir = OUT_DIR / "smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    export_path = smoke_dir / "export_ids.txt"
    output_path = smoke_dir / "cli_output.txt"

    input_lines = [
        "1",
        "a-123 abc-1234 abcd-1234 efgh5678",
        "2",
        "abc-1234",
        "2",
        "zz-9999",
        "8",
        str(export_path),
        "0",
    ]
    input_text = "\n".join(input_lines) + "\n"

    proc = subprocess.run(
        [str(exe_full_path)],
        input=input_text,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    cli_output = (proc.stdout or "") + (proc.stderr or "")
    output_path.write_text(cli_output, encoding="utf-8")
    if proc.returncode != 0:
        raise AssertionError(f"Assertion failed [exit_code]. Return code: {proc.returncode}")

    if not export_path.exists():
        raise AssertionError(f"Assertion failed [export_exists]. File not found: {export_path}")

    actual = sorted({line.strip() for line in export_path.read_text(encoding="utf-8").splitlines() if line.strip()})
    expected = sorted({"a123", "abc1234", "abcd1234", "efgh5678"})
    if actual != expected:
        raise AssertionError(
            "Assertion failed [export_content]. "
            f"Expected: {', '.join(expected)}; Actual: {', '.join(actual)}"
        )

    print("CLI smoke test passed.")
    print(f"Output log: {output_path}")
    print(f"Export file: {export_path}")
    return 0
