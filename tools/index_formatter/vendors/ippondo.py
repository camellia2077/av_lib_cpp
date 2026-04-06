from __future__ import annotations

from typing import Optional

from ..core.patterns import (
    IPPONDO_STRICT_PATTERN,
    IPPONDO_TAGGED_PATTERN,
    IPPONDO_VARIANT_PATTERN,
)


def parse_ippondo_code(stem: str) -> Optional[str]:
    # 1Pondo format (strict):
    # - Input: YYYYMM_NNN, e.g. 012026_234
    # - Output: YYYYMM_NNN-1pondo
    # Keep idempotent when suffix already exists: YYYYMM_NNN-1pondo
    if IPPONDO_TAGGED_PATTERN.fullmatch(stem):
        prefix = stem.split("-")[0]
        return f"{prefix}-1pondo"
    if IPPONDO_STRICT_PATTERN.fullmatch(stem):
        return f"{stem}-1pondo"
    variant_match = IPPONDO_VARIANT_PATTERN.fullmatch(stem)
    if variant_match:
        return f"{variant_match.group(1)}-1pondo"
    return None
