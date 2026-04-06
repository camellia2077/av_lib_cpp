from __future__ import annotations

import re
from typing import Optional

CARIB_HINT_PATTERN = re.compile(r"carib(?:bean)?", re.IGNORECASE)
CARIB_DATE_CODE_SEARCH_PATTERN = re.compile(
    r"(?<!\d)(\d{6})-(\d{3})(?!\d)",
    re.IGNORECASE,
)


def parse_carib_date_code(stem: str) -> Optional[str]:
    # Conservative Carib detection:
    # - Require vendor hint ("carib" / "caribbean") somewhere in the stem.
    # - Require a date code token like YYMMDD-NNN somewhere in the stem.
    # This avoids broad false positives from generic date-like strings.
    if not CARIB_HINT_PATTERN.search(stem):
        return None

    matched = CARIB_DATE_CODE_SEARCH_PATTERN.search(stem)
    if not matched:
        return None
    return f"{matched.group(1)}-{matched.group(2)}-carib"
