from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .patterns import (
    COMPACT_CODE_PATTERN,
    COMPACT_CODE_WITH_PART_PATTERN,
    HYPHENATED_CODE_PATTERN,
    PART_DIRECT_LETTER_PATTERN,
    PART_WITH_SEP_PATTERN,
    TITLE_TRAILING_NUMERIC_PART_PATTERN,
)
from ..vendors import (
    parse_carib_date_code,
    parse_heyzo_code,
    parse_ippondo_code,
    parse_tokyo_hot_code,
)

ParseRuleFn = Callable[[str], Optional[str]]


@dataclass(frozen=True)
class ParseRule:
    name: str
    priority: int
    apply: ParseRuleFn


def _extract_part_from_suffix(suffix: str) -> Optional[str]:
    part_match = PART_WITH_SEP_PATTERN.fullmatch(suffix)
    if part_match:
        return part_match.group(1).upper()

    part_direct_match = PART_DIRECT_LETTER_PATTERN.fullmatch(suffix)
    if part_direct_match:
        return part_direct_match.group(1).upper()

    return None


def _extract_part_from_verbose_suffix(suffix: str) -> Optional[str]:
    matched = TITLE_TRAILING_NUMERIC_PART_PATTERN.fullmatch(suffix)
    if matched:
        return matched.group(1)
    return None


def _render_code(prefix: str, number: str, part: Optional[str] = None) -> str:
    base = f"{prefix.upper()}-{number}"
    if part:
        return f"{base}-{part.upper()}"
    return base


def parse_hyphenated_code(stem: str) -> Optional[str]:
    matched = HYPHENATED_CODE_PATTERN.search(stem)
    if not matched:
        return None

    prefix, number = matched.group(1), matched.group(2)
    suffix = stem[matched.end() :]
    part = _extract_part_from_suffix(suffix)
    if not part:
        part = _extract_part_from_verbose_suffix(suffix)
    return _render_code(prefix, number, part)


def parse_compact_code_with_part(stem: str) -> Optional[str]:
    matched = COMPACT_CODE_WITH_PART_PATTERN.search(stem)
    if not matched:
        return None

    prefix, number, part = matched.group(1), matched.group(2), matched.group(3)
    return _render_code(prefix, number, part)


def parse_compact_code(stem: str) -> Optional[str]:
    matched = COMPACT_CODE_PATTERN.search(stem)
    if not matched:
        return None

    prefix, number = matched.group(1), matched.group(2)
    return _render_code(prefix, number)


PARSE_RULES = sorted(
    [
        ParseRule(name="ippondo-code", priority=1, apply=parse_ippondo_code),
        ParseRule(name="tokyo-hot-code", priority=2, apply=parse_tokyo_hot_code),
        ParseRule(name="heyzo-code", priority=3, apply=parse_heyzo_code),
        ParseRule(name="carib-date-code", priority=5, apply=parse_carib_date_code),
        ParseRule(name="hyphenated-code", priority=10, apply=parse_hyphenated_code),
        ParseRule(
            name="compact-code-with-part",
            priority=20,
            apply=parse_compact_code_with_part,
        ),
        ParseRule(name="compact-code", priority=30, apply=parse_compact_code),
    ],
    key=lambda r: r.priority,
)


def run_parse_rules(stem: str) -> tuple[Optional[str], Optional[str]]:
    for rule in PARSE_RULES:
        parsed = rule.apply(stem)
        if parsed:
            return parsed, rule.name
    return None, None
