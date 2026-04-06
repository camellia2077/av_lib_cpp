from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from .executor import delete_source_file, execute_action
from .planner import build_folder_plans, list_unmatched_input_folders
from .policy import is_folder_empty_or_junk


@dataclass(frozen=True)
class MergeSummary:
    matched_folders: int
    planned_actions: int
    succeeded_actions: int


def run_merge(input_dir: Path, output_dir: Path, apply: bool) -> MergeSummary:
    mode_prefix = "[执行]" if apply else "[预览]"
    print(f"当前模式: {mode_prefix}")
    print("-" * 50)

    plans = build_folder_plans(input_dir, output_dir)
    unmatched_input_folders = list_unmatched_input_folders(input_dir, output_dir)
    if not plans and not unmatched_input_folders:
        print("没有找到可处理的文件夹。")
        return MergeSummary(matched_folders=0, planned_actions=0, succeeded_actions=0)

    planned_actions = 0
    succeeded_actions = 0

    for plan in plans:
        print(f"扫描到匹配文件夹: '{plan.name}' (包含 {len(plan.actions)} 个视频)")
        folder_success = 0
        for action in plan.actions:
            planned_actions += 1
            if apply:
                ok, message = execute_action(action)
                print(message)
                if ok:
                    folder_success += 1
                    succeeded_actions += 1
                    _, warn = delete_source_file(action.source)
                    if warn:
                        print(warn)
            else:
                if action.kind == "skip_exists":
                    print(f"  └── 跳过 (已存在): {action.source.name}")
                else:
                    print(f"  └── 计划复制: {action.source.name}")
                folder_success += 1
                succeeded_actions += 1

        if folder_success == len(plan.actions):
            if apply:
                if is_folder_empty_or_junk(plan.input_folder):
                    try:
                        shutil.rmtree(plan.input_folder)
                        print(f"删除空文件夹: '{plan.input_folder.name}'\n")
                    except Exception as exc:  # noqa: BLE001
                        print(f"删除文件夹失败: '{plan.input_folder.name}' ({exc})\n")
                else:
                    print(f"[警告] 文件夹 '{plan.name}' 内仍有非视频文件，已保留该文件夹。\n")
            else:
                print(
                    "计划检查并删除 input 文件夹 "
                    f"(若清空视频后无其他文件): '{plan.input_folder.name}'\n"
                )
        else:
            print(f"[警告] 文件夹 '{plan.name}' 中有视频未成功处理，跳过删除。\n")

    # 业务意图:
    # - 同名目录: 走“目录内视频同步/清理”细粒度逻辑（上方 plans 分支）
    # - 无同名目录: 直接整目录迁移到 output，避免遗漏未匹配目录内容
    for in_folder in unmatched_input_folders:
        target_folder = output_dir / in_folder.name
        planned_actions += 1
        if apply:
            try:
                if target_folder.exists():
                    print(
                        f"[警告] 跳过整目录迁移，目标已存在: '{in_folder.name}' -> {target_folder}"
                    )
                else:
                    shutil.move(str(in_folder), str(target_folder))
                    succeeded_actions += 1
                    print(f"已整目录迁移: '{in_folder.name}' -> {target_folder}\n")
            except Exception as exc:  # noqa: BLE001
                print(f"整目录迁移失败: '{in_folder.name}' ({exc})\n")
        else:
            succeeded_actions += 1
            print(f"计划整目录迁移: '{in_folder.name}' -> {target_folder}\n")

    print("-" * 50)
    print("任务结束。")
    if not apply:
        print("提示: 以上仅为预览。如需实际执行，请在命令后加上 --apply 参数。")

    return MergeSummary(
        matched_folders=len(plans),
        planned_actions=planned_actions,
        succeeded_actions=succeeded_actions,
    )
