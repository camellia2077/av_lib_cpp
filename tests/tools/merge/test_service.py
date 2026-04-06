from pathlib import Path

from tools.merge.app.service import run_merge


def test_run_merge_apply_copies_and_cleans_folder(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    in_actor = input_dir / "ActorA"
    out_actor = output_dir / "ActorA"
    in_actor.mkdir(parents=True)
    out_actor.mkdir(parents=True)

    source = in_actor / "abc-123.mp4"
    source.write_bytes(b"video-data")

    summary = run_merge(input_dir=input_dir, output_dir=output_dir, apply=True)

    assert summary.matched_folders == 1
    assert summary.planned_actions == 1
    assert summary.succeeded_actions == 1
    assert not source.exists()
    assert (out_actor / "abc-123.mp4").exists()
    assert not in_actor.exists()


def test_run_merge_apply_moves_unmatched_folder_as_whole(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    unmatched_in = input_dir / "ActorOnlyInInput"
    unmatched_in.mkdir(parents=True)
    (output_dir / "Other").mkdir(parents=True)
    (unmatched_in / "movie-001.mp4").write_bytes(b"video")

    summary = run_merge(input_dir=input_dir, output_dir=output_dir, apply=True)

    moved_target = output_dir / "ActorOnlyInInput"
    assert summary.matched_folders == 0
    assert summary.planned_actions == 1
    assert summary.succeeded_actions == 1
    assert not unmatched_in.exists()
    assert (moved_target / "movie-001.mp4").exists()
