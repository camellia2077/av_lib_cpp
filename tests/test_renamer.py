from pathlib import Path

import pytest

from tools.index_formatter.config import DirectoryCase, load_sanitize_cases
from tools.index_formatter.core.renamer import is_video, process

SANITIZE_CASES = load_sanitize_cases()


def test_is_video_by_extension(tmp_path: Path) -> None:
    video_path = tmp_path / "sample.mp4"
    text_path = tmp_path / "sample.txt"
    video_path.write_text("x", encoding="utf-8")
    text_path.write_text("x", encoding="utf-8")

    assert is_video(video_path) is True
    assert is_video(text_path) is False


@pytest.mark.parametrize(
    "case",
    SANITIZE_CASES.directory_cases,
    ids=[case.name for case in SANITIZE_CASES.directory_cases],
)
def test_process_directory_cases(case: DirectoryCase, tmp_path: Path) -> None:
    for file_name in case.initial_files:
        (tmp_path / file_name).write_text("x", encoding="utf-8")

    scanned, renamed = process(tmp_path, apply_changes=case.apply_changes)

    assert scanned == case.expected_scanned
    assert renamed == case.expected_renamed

    for file_name in case.expected_present_files:
        assert (tmp_path / file_name).exists(), file_name

    for file_name in case.expected_absent_files:
        assert not (tmp_path / file_name).exists(), file_name


def test_preview_simulates_collision_suffixes_like_apply(tmp_path: Path, capsys) -> None:
    files = [
        "MVSD-294 Lena Aoi, Maki Hoshikawa - Real Semen Lovers - AI REMASTER - 1.mkv",
        "MVSD-294 Lena Aoi, Maki Hoshikawa - Real Semen Lovers - AI REMASTER - 2.mkv",
        "MVSD-294 Lena Aoi, Maki Hoshikawa - Real Semen Lovers - AI REMASTER - 3.mkv",
    ]
    for file_name in files:
        (tmp_path / file_name).write_text("x", encoding="utf-8")

    scanned, renamed = process(tmp_path, apply_changes=False)
    output = capsys.readouterr().out

    assert scanned == 3
    assert renamed == 3
    assert "-> MVSD-294-1.mkv" in output
    assert "-> MVSD-294-2.mkv" in output
    assert "-> MVSD-294-3.mkv" in output

    for file_name in files:
        assert (tmp_path / file_name).exists(), file_name


def test_preview_color_mode_marks_expected_vs_unexpected(tmp_path: Path, capsys) -> None:
    (tmp_path / "oks-168.mp4").write_text("x", encoding="utf-8")
    (tmp_path / "ssis00663hhb_60fps_000.mp4").write_text("x", encoding="utf-8")

    process(tmp_path, apply_changes=False, color="always")
    output = capsys.readouterr().out

    assert "\x1b[33moks-168.mp4 -> OKS-168.mp4" in output
    assert (
        "\x1b[31mssis00663hhb_60fps_000.mp4 -> ssis00663hhb60fps000.mp4" in output
    )


def test_apply_never_uses_color_codes_even_if_forced(tmp_path: Path, capsys) -> None:
    (tmp_path / "oks-168.mp4").write_text("x", encoding="utf-8")

    process(tmp_path, apply_changes=True, color="always")
    output = capsys.readouterr().out

    assert "\x1b[" not in output

