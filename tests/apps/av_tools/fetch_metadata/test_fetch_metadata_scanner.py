from pathlib import Path

from apps.av_tools.fetch_metadata.scanner import collect_video_files


def test_collect_video_files_recursively_from_directory(tmp_path: Path) -> None:
    root_video = tmp_path / "A-100.mp4"
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    nested_video = nested_dir / "B-200.mkv"
    ignored_file = nested_dir / "note.txt"
    root_video.write_text("x", encoding="utf-8")
    nested_video.write_text("x", encoding="utf-8")
    ignored_file.write_text("x", encoding="utf-8")

    files, failures = collect_video_files(tmp_path)

    assert failures == []
    assert [path.name for path in files] == ["A-100.mp4", "B-200.mkv"]


def test_collect_video_files_for_single_video_file(tmp_path: Path) -> None:
    file_path = tmp_path / "ABC-123.mp4"
    file_path.write_text("x", encoding="utf-8")

    files, failures = collect_video_files(file_path)

    assert failures == []
    assert files == [file_path.resolve()]


def test_collect_video_files_marks_non_video_input_file_as_invalid(tmp_path: Path) -> None:
    file_path = tmp_path / "not_video.txt"
    file_path.write_text("x", encoding="utf-8")

    files, failures = collect_video_files(file_path)

    assert files == []
    assert len(failures) == 1
    assert failures[0].reason == "INVALID_INPUT"

