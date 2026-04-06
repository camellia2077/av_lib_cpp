from apps.av_tools.index_formatter.config import (
    CoreMappingCase,
    RuleTraceCase,
    SanitizeCases,
    load_sanitize_cases,
)
from apps.av_tools.index_formatter.core.engine import sanitize_stem, sanitize_stem_with_meta

SANITIZE_CASES: SanitizeCases = load_sanitize_cases()


def _mapping_case_id(case: CoreMappingCase) -> str:
    return case.raw_stem


def _rule_trace_case_id(case: RuleTraceCase) -> str:
    return case.raw_stem


def test_sanitize_cases_loaded() -> None:
    assert SANITIZE_CASES.core_mappings
    assert SANITIZE_CASES.idempotency_raw_stems
    assert SANITIZE_CASES.rule_trace
    assert SANITIZE_CASES.directory_cases


def test_sanitize_stem_core_mappings() -> None:
    for case in SANITIZE_CASES.core_mappings:
        assert sanitize_stem(case.raw_stem) == case.expected, _mapping_case_id(case)


def test_sanitize_stem_is_idempotent() -> None:
    for raw_stem in SANITIZE_CASES.idempotency_raw_stems:
        first = sanitize_stem(raw_stem)
        second = sanitize_stem(first)
        assert second == first, raw_stem


def test_sanitize_stem_rule_trace() -> None:
    for case in SANITIZE_CASES.rule_trace:
        result = sanitize_stem_with_meta(case.raw_stem)
        assert result.value == case.expected_value, _rule_trace_case_id(case)
        assert result.parse_rule == case.expected_rule, _rule_trace_case_id(case)
        assert result.is_exempt is case.is_exempt, _rule_trace_case_id(case)
        assert result.used_fallback is case.used_fallback, _rule_trace_case_id(case)


def test_sanitize_stem_keeps_trailing_numeric_part_from_verbose_title() -> None:
    raw = "MVSD-294 Lena Aoi, Maki Hoshikawa - Real Semen Lovers - AI REMASTER - 2"
    assert sanitize_stem(raw) == "MVSD-294-2"

