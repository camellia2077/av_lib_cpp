from __future__ import annotations

import re
from typing import Optional

HEYZO_CODE_PATTERN = re.compile(
    r"^\s*heyzo(?:[-_.](?:2160p|1080p|720p|4k|fhd|uhd|hd|sd))*[-_.]?(\d{4})(?:[-_.][a-z0-9]+)*\s*$",
    re.IGNORECASE,
)


def parse_heyzo_code(stem: str) -> Optional[str]:
    # Heyzo format:
    # - Input may include quality tokens and trailing tags, e.g.
    #   heyzo_hd_0904 / heyzo_hd_0904_full
    # - Output normalized to HEYZO-NNNN, e.g. HEYZO-0904
    matched = HEYZO_CODE_PATTERN.fullmatch(stem)
    if not matched:
        return None
    return f"HEYZO-{matched.group(1)}"
