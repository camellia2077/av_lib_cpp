from __future__ import annotations

import re

from ..index_formatter.core.engine import sanitize_stem_with_meta

PART_SUFFIX_PATTERN = re.compile(r"^([A-Z]{2,10}-\d{2,6})-(?:[A-Z]|\d+)$")


def _to_api_query_code(normalized_code: str) -> str:
    # Split files often carry a synthetic part suffix (e.g. IPSD-048-A,
    # MVSD-294-2). The API generally indexes the base movie id only, so we
    # strip that suffix for fetch-metadata requests to improve hit rate.
    matched = PART_SUFFIX_PATTERN.fullmatch(normalized_code)
    if matched:
        return matched.group(1)
    return normalized_code


def extract_standard_movie_code(stem: str) -> str | None:
    result = sanitize_stem_with_meta(stem)
    if result.used_fallback:
        return None
    if not result.parse_rule:
        return None
    return _to_api_query_code(result.value)
