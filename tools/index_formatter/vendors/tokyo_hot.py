from __future__ import annotations

import re
from typing import Optional

TOKYO_HOT_CODE_PATTERN = re.compile(
    r"^\s*([nN]\d{4})(?:[-_.].*)?\s*$",
    re.IGNORECASE,
)


def parse_tokyo_hot_code(stem: str) -> Optional[str]:
    # Tokyo Hot format:
    # - Input often starts with nNNNN plus extra performer/quality tokens,
    #   e.g. n1039_kaori_shiraishi_eb_n_fhd
    # - Output normalized to TOKYO-HOT-NNNNN, e.g. TOKYO-HOT-N1039
    matched = TOKYO_HOT_CODE_PATTERN.fullmatch(stem)
    if not matched:
        return None
    return f"TOKYO-HOT-{matched.group(1).upper()}"
