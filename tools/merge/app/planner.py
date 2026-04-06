from __future__ import annotations

from pathlib import Path

from .models import FolderPlan, VideoAction
from .policy import is_video


def build_folder_plans(input_dir: Path, output_dir: Path) -> list[FolderPlan]:
    input_folders = {p.name: p for p in input_dir.iterdir() if p.is_dir()}
    output_folders = {p.name: p for p in output_dir.iterdir() if p.is_dir()}
    common_folder_names = sorted(set(input_folders.keys()).intersection(output_folders.keys()))

    plans: list[FolderPlan] = []
    for folder_name in common_folder_names:
        in_folder = input_folders[folder_name]
        out_folder = output_folders[folder_name]
        videos = sorted([p for p in in_folder.iterdir() if p.is_file() and is_video(p)])
        if not videos:
            continue

        actions: list[VideoAction] = []
        for video_in in videos:
            video_out = out_folder / video_in.name
            if video_out.exists():
                actions.append(VideoAction(kind="skip_exists", source=video_in, target=video_out))
            else:
                actions.append(VideoAction(kind="copy", source=video_in, target=video_out))
        plans.append(
            FolderPlan(
                name=folder_name,
                input_folder=in_folder,
                output_folder=out_folder,
                actions=actions,
            )
        )
    return plans


def list_unmatched_input_folders(input_dir: Path, output_dir: Path) -> list[Path]:
    input_folders = {p.name: p for p in input_dir.iterdir() if p.is_dir()}
    output_folders = {p.name: p for p in output_dir.iterdir() if p.is_dir()}
    unmatched_names = sorted(set(input_folders.keys()) - set(output_folders.keys()))
    return [input_folders[name] for name in unmatched_names]
