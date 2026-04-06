from __future__ import annotations

from ..config.config_loader import load_rules_config
from ..config.config_models import RulesConfig, SanitizeResult
from .patterns import ALLOWED_PATTERN
from .rules_parse import run_parse_rules
from .rules_preprocess import run_preprocess_rules

RULES_CONFIG = load_rules_config()


def sanitize_stem(stem: str, config: RulesConfig = RULES_CONFIG) -> str:
    return sanitize_stem_with_meta(stem, config=config).value


def sanitize_stem_with_meta(
    stem: str, config: RulesConfig = RULES_CONFIG
) -> SanitizeResult:
    normalized = run_preprocess_rules(stem, config=config)

    special_case = config.special_cases.get(normalized)
    if special_case:
        return SanitizeResult(value=special_case, parse_rule="special-case-exact")

    parsed, parse_rule = run_parse_rules(normalized)
    if parsed:
        return SanitizeResult(value=parsed, parse_rule=parse_rule)

    cleaned = ALLOWED_PATTERN.sub("", normalized)
    if not cleaned:
        cleaned = "VIDEO"
    return SanitizeResult(value=cleaned, used_fallback=True)
