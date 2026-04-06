from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RulesConfig:
    special_remove_tokens: list[str]
    trailing_stem_labels: list[str]
    special_cases: dict[str, str]
    trailing_stem_label_pattern: re.Pattern[str]


@dataclass(frozen=True)
class SanitizeResult:
    value: str
    parse_rule: Optional[str] = None
    is_exempt: bool = False
    used_fallback: bool = False


@dataclass(frozen=True)
class CoreMappingCase:
    raw_stem: str
    expected: str


@dataclass(frozen=True)
class RuleTraceCase:
    raw_stem: str
    expected_value: str
    expected_rule: Optional[str]
    is_exempt: bool
    used_fallback: bool


@dataclass(frozen=True)
class DirectoryCase:
    name: str
    apply_changes: bool
    initial_files: list[str]
    expected_present_files: list[str]
    expected_absent_files: list[str]
    expected_scanned: int
    expected_renamed: int


@dataclass(frozen=True)
class SanitizeCases:
    core_mappings: list[CoreMappingCase]
    idempotency_raw_stems: list[str]
    rule_trace: list[RuleTraceCase]
    directory_cases: list[DirectoryCase]
