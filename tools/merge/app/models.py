from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


ActionType = Literal["skip_exists", "copy"]


@dataclass(frozen=True)
class VideoAction:
    kind: ActionType
    source: Path
    target: Path


@dataclass(frozen=True)
class FolderPlan:
    name: str
    input_folder: Path
    output_folder: Path
    actions: list[VideoAction]

