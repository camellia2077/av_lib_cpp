from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..config.config_models import RulesConfig

PreprocessRuleFn = Callable[[str, RulesConfig], str]


@dataclass(frozen=True)
class PreprocessRule:
    name: str
    priority: int
    apply: PreprocessRuleFn


def preprocess_remove_special_tokens(stem: str, config: RulesConfig) -> str:
    normalized = stem
    for token in config.special_remove_tokens:
        normalized = normalized.replace(token, "")
    return normalized


def preprocess_strip_trailing_stem_labels(stem: str, config: RulesConfig) -> str:
    return config.trailing_stem_label_pattern.sub("", stem)


PREPROCESS_RULES = sorted(
    [
        PreprocessRule(
            name="remove-special-noise-tokens",
            priority=10,
            apply=preprocess_remove_special_tokens,
        ),
        PreprocessRule(
            name="strip-trailing-stem-labels",
            priority=20,
            apply=preprocess_strip_trailing_stem_labels,
        ),
    ],
    key=lambda r: r.priority,
)


def run_preprocess_rules(stem: str, config: RulesConfig) -> str:
    normalized = stem.strip()
    for rule in PREPROCESS_RULES:
        normalized = rule.apply(normalized, config).strip()
    return normalized
