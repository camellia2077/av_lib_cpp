from __future__ import annotations

import re
from dataclasses import dataclass

from ..fetch_metadata.parser import extract_standard_movie_code

SPLIT_CODE_PATTERN = re.compile(r"^([A-Z]{2,10})-(\d{2,6})$")
LEADING_DIGIT_PREFIX_PATTERN = re.compile(r"^[0-9][A-Z]+[-_A-Z0-9]+$")
CARIB_SUFFIX_PATTERN = re.compile(r"^(\d{6}-\d{2,4})-carib$", re.IGNORECASE)
IPPONDO_SUFFIX_PATTERN = re.compile(r"^(\d{6}_\d{3})-1pondo$", re.IGNORECASE)
DATE_HYPHEN_PATTERN = re.compile(r"^(\d{6}-\d{2,4})$")
DATE_UNDERSCORE_PATTERN = re.compile(r"^(\d{6}_\d{3})$")
HEYZO_CANONICAL_PATTERN = re.compile(r"^HEYZO-\d{4}$", re.IGNORECASE)
TOKYO_HOT_CANONICAL_PATTERN = re.compile(r"^TOKYO-HOT-[A-Z]\d{4}$", re.IGNORECASE)


@dataclass(frozen=True)
class Candidate:
    code: str
    url: str
    title: str = ""
    cover: str = ""


def levenshtein_distance(source: str, target: str) -> int:
    if source == target:
        return 0
    if not source:
        return len(target)
    if not target:
        return len(source)
    prev = list(range(len(target) + 1))
    for i, s_char in enumerate(source, start=1):
        curr = [i]
        for j, t_char in enumerate(target, start=1):
            cost = 0 if s_char == t_char else 1
            curr.append(
                min(
                    prev[j] + 1,      # delete
                    curr[j - 1] + 1,  # insert
                    prev[j - 1] + cost,  # replace
                )
            )
        prev = curr
    return prev[-1]


def expand_query_keys(movie_code: str) -> list[str]:
    canonical = movie_code.strip().upper()
    keys: list[str] = []

    def add(value: str) -> None:
        candidate = value.strip()
        if not candidate:
            return
        if candidate in keys:
            return
        keys.append(candidate)

    add(canonical)
    if LEADING_DIGIT_PREFIX_PATTERN.match(canonical):
        add(canonical[1:])

    matched = SPLIT_CODE_PATTERN.fullmatch(canonical)
    if not matched:
        add(canonical.replace("-", ""))
        add(canonical.replace("-", "_"))
        return keys

    prefix = matched.group(1)
    number = matched.group(2)
    number_variants = [number]
    stripped = number.lstrip("0")
    if stripped:
        for i in range(0, len(number) - len(stripped) + 1):
            number_variants.append(("0" * i) + stripped)
    else:
        number_variants.append("0")

    separators = ["-", "_", "", " "]
    for n in number_variants:
        for sep in separators:
            add(f"{prefix}{sep}{n}")
    return keys


def select_best_candidate(
    target_code: str,
    candidates: list[Candidate],
) -> Candidate | None:
    canonical = _normalize_match_code(target_code)
    exact_candidates: list[Candidate] = []
    for candidate in candidates:
        normalized = _normalize_match_code(candidate.code)
        if normalized == canonical:
            exact_candidates.append(candidate)

    if not exact_candidates:
        return None
    if len(exact_candidates) == 1:
        return exact_candidates[0]

    # Tie-break candidates that normalize to the same canonical id by choosing
    # the raw code that is closest to the target representation.
    ranked = sorted(
        exact_candidates,
        key=lambda item: (
            levenshtein_distance(_normalize_match_code(item.code), canonical),
            len(item.code),
            item.url,
        ),
    )
    return ranked[0]


def _normalize_match_code(raw: str) -> str:
    value = raw.strip().upper()
    normalized = extract_standard_movie_code(value)
    if normalized:
        return normalized

    # Vendor canonical forms below are intentionally kept as-is. They are
    # normalized by vendor rules already and don't fit generic AA-123 patterns.
    if HEYZO_CANONICAL_PATTERN.fullmatch(value):
        return value
    if TOKYO_HOT_CANONICAL_PATTERN.fullmatch(value):
        return value

    matched = CARIB_SUFFIX_PATTERN.fullmatch(value)
    if matched:
        return matched.group(1).upper()

    matched = IPPONDO_SUFFIX_PATTERN.fullmatch(value)
    if matched:
        return matched.group(1).upper()

    matched = DATE_HYPHEN_PATTERN.fullmatch(value)
    if matched:
        return matched.group(1).upper()

    matched = DATE_UNDERSCORE_PATTERN.fullmatch(value)
    if matched:
        return matched.group(1).upper()

    return value
