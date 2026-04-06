from pathlib import Path

from apps.av_tools.move_by_actor.app.scanner import extract_movie_code, scan_items_for_move


def test_extract_movie_code_supports_hyphenated_and_compact() -> None:
    assert extract_movie_code("abc-123") == "ABC-123"
    assert extract_movie_code("abc123") == "ABC-123"
    assert extract_movie_code("no_code_here") is None


def test_scan_items_for_move_non_recursive_reads_video_files_only(tmp_path: Path) -> None:
    (tmp_path / "BETA-200.mkv").write_text("x", encoding="utf-8")
    (tmp_path / "alpha100.mp4").write_text("x", encoding="utf-8")
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")

    items = scan_items_for_move(tmp_path, recursive=False)

    assert [item.path.name for item in items] == ["alpha100.mp4", "BETA-200.mkv"]
    assert items[0].code_hint == "ALPHA-100"
    assert items[1].code_hint == "BETA-200"
    assert all(not item.is_dir for item in items)


def test_scan_items_for_move_recursive_moves_video_folder_as_unit(tmp_path: Path) -> None:
    (tmp_path / "root-001.mp4").write_text("x", encoding="utf-8")
    actor_folder = tmp_path / "MIZD-374"
    actor_folder.mkdir()
    (actor_folder / "anything.mp4").write_text("x", encoding="utf-8")
    nested = actor_folder / "nested"
    nested.mkdir()
    (nested / "inside.mp4").write_text("x", encoding="utf-8")

    items = scan_items_for_move(tmp_path, recursive=True)

    assert len(items) == 2
    file_item = next(item for item in items if not item.is_dir)
    folder_item = next(item for item in items if item.is_dir)

    assert file_item.path.name == "root-001.mp4"
    assert file_item.code_hint == "ROOT-001"
    assert folder_item.path == actor_folder
    assert folder_item.code_hint == "MIZD-374"

