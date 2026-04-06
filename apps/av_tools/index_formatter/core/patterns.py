from __future__ import annotations

import re

# Keep only English letters, digits, and '-'
ALLOWED_PATTERN = re.compile(r"[^A-Za-z0-9-]+")

# Parse canonical codes like SDDE-538 and optional part suffixes.
HYPHENATED_CODE_PATTERN = re.compile(r"([A-Za-z]{2,10})-(\d{2,6})")

# Parse compact codes like IPSD048A / SDDE538.
COMPACT_CODE_WITH_PART_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z]{2,10})(\d{2,6})([A-Za-z])(?![A-Za-z0-9])",
    re.IGNORECASE,
)
COMPACT_CODE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z]{2,10})(\d{2,6})(?![A-Za-z0-9])",
    re.IGNORECASE,
)

# Part suffix patterns after base code extraction.
PART_WITH_SEP_PATTERN = re.compile(r"^\s*[-_]\s*([A-Za-z]|\d+)\s*$")
PART_DIRECT_LETTER_PATTERN = re.compile(r"^\s*([A-Za-z])\s*$")
# Extract trailing numeric part from a verbose title tail, e.g.
# "MVSD-294 ... - AI REMASTER - 2" -> "2".
TITLE_TRAILING_NUMERIC_PART_PATTERN = re.compile(r"^.*[-_]\s*(\d+)\s*$")

# Strict 1Pondo formats
IPPONDO_STRICT_PATTERN = re.compile(r"^\d{6}_\d{3}$")
IPPONDO_TAGGED_PATTERN = re.compile(r"^\d{6}_\d{3}-1pondo$", re.IGNORECASE)
# Accept common noisy 1Pondo variants like:
# - YYYYMM_NNN-1pon
# - YYYYMM_NNN-1pon-1080p
# - YYYYMM_NNN-1pondo-anything
IPPONDO_VARIANT_PATTERN = re.compile(
    r"^(\d{6}_\d{3})-1pon(?:do)?(?:[-_].*)?$",
    re.IGNORECASE,
)


def build_trailing_stem_label_pattern(labels: list[str]) -> re.Pattern[str]:
    escaped = [re.escape(label) for label in labels if label]
    if not escaped:
        return re.compile(r"(?!x)x")
    alternatives = "|".join(sorted(escaped, key=len, reverse=True))
    return re.compile(rf"(?:\.(?:{alternatives}))+$", re.IGNORECASE)
