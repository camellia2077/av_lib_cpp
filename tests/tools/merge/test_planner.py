from pathlib import Path

from tools.merge.app.planner import build_folder_plans, list_unmatched_input_folders


def test_build_folder_plans_creates_actions_for_common_folder(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    (input_dir / "A").mkdir(parents=True)
    (input_dir / "B").mkdir(parents=True)
    (output_dir / "A").mkdir(parents=True)
    (output_dir / "C").mkdir(parents=True)

    src_video = input_dir / "A" / "abc-123.mp4"
    src_video.write_text("x", encoding="utf-8")
    existing_video = output_dir / "A" / "abc-123.mp4"
    existing_video.write_text("x", encoding="utf-8")

    plans = build_folder_plans(input_dir=input_dir, output_dir=output_dir)
    assert len(plans) == 1
    assert plans[0].name == "A"
    assert len(plans[0].actions) == 1
    assert plans[0].actions[0].kind == "skip_exists"


def test_list_unmatched_input_folders_returns_input_only_folders(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    (input_dir / "A").mkdir(parents=True)
    (input_dir / "B").mkdir(parents=True)
    (output_dir / "A").mkdir(parents=True)

    unmatched = list_unmatched_input_folders(input_dir=input_dir, output_dir=output_dir)
    assert [p.name for p in unmatched] == ["B"]
