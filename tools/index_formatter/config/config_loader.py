from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Python 3.11+ is required for TOML support (tomllib missing)."
    ) from exc

from .config_models import (
    CoreMappingCase,
    DirectoryCase,
    RuleTraceCase,
    RulesConfig,
    SanitizeCases,
)
from ..core.patterns import build_trailing_stem_label_pattern

SANITIZE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = SANITIZE_DIR / "config"
RULES_CONFIG_PATH = CONFIG_DIR / "sanitize_rules.toml"
CASES_DIR = CONFIG_DIR / "cases"
VENDOR_CASES_DIR = CASES_DIR / "vendors"
CORE_MAPPINGS_CASES_PATH = CASES_DIR / "core_mappings.toml"
IDEMPOTENCY_CASES_PATH = CASES_DIR / "idempotency.toml"
RULE_TRACE_CASES_PATH = CASES_DIR / "rule_trace.toml"
DIRECTORY_CASES_PATH = CASES_DIR / "directory_cases.toml"

def _as_str_list(raw: Any, default: list[str]) -> list[str]:
    if not isinstance(raw, list):
        return default
    cleaned = [str(item) for item in raw if str(item).strip()]
    return cleaned or default


def _as_str_map(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


def _to_core_mapping_case(raw: object) -> CoreMappingCase:
    if not isinstance(raw, dict):
        raise ValueError("Each [core_mappings] entry must be a table.")
    return CoreMappingCase(raw_stem=str(raw["raw_stem"]), expected=str(raw["expected"]))


def _to_rule_trace_case(raw: object) -> RuleTraceCase:
    if not isinstance(raw, dict):
        raise ValueError("Each [rule_trace] entry must be a table.")
    expected_rule = raw.get("expected_rule")
    return RuleTraceCase(
        raw_stem=str(raw["raw_stem"]),
        expected_value=str(raw["expected_value"]),
        expected_rule=None if expected_rule is None else str(expected_rule),
        is_exempt=bool(raw["is_exempt"]),
        used_fallback=bool(raw["used_fallback"]),
    )


def _to_directory_case(raw: object) -> DirectoryCase:
    if not isinstance(raw, dict):
        raise ValueError("Each [directory_cases] entry must be a table.")

    initial_files = raw.get("initial_files", [])
    expected_present_files = raw.get("expected_present_files", [])
    expected_absent_files = raw.get("expected_absent_files", [])
    if not isinstance(initial_files, list):
        raise ValueError("`directory_cases.initial_files` must be a list.")
    if not isinstance(expected_present_files, list):
        raise ValueError("`directory_cases.expected_present_files` must be a list.")
    if not isinstance(expected_absent_files, list):
        raise ValueError("`directory_cases.expected_absent_files` must be a list.")

    return DirectoryCase(
        name=str(raw["name"]),
        apply_changes=bool(raw["apply_changes"]),
        initial_files=[str(item) for item in initial_files],
        expected_present_files=[str(item) for item in expected_present_files],
        expected_absent_files=[str(item) for item in expected_absent_files],
        expected_scanned=int(raw["expected_scanned"]),
        expected_renamed=int(raw["expected_renamed"]),
    )


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        data = tomllib.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a TOML table.")
    return data


def load_rules_config(config_path: Path = RULES_CONFIG_PATH) -> RulesConfig:
    if not config_path.exists():
        return RulesConfig(
            special_remove_tokens=[],
            trailing_stem_labels=[],
            special_cases={},
            trailing_stem_label_pattern=build_trailing_stem_label_pattern([]),
        )

    with config_path.open("rb") as f:
        data = tomllib.load(f)

    sanitize_section = data.get("sanitize", {})
    special_remove_tokens = _as_str_list(
        sanitize_section.get("special_remove_tokens"),
        [],
    )
    trailing_stem_labels = _as_str_list(
        sanitize_section.get("trailing_stem_labels"),
        [],
    )
    return RulesConfig(
        special_remove_tokens=special_remove_tokens,
        trailing_stem_labels=trailing_stem_labels,
        special_cases=_as_str_map(data.get("special_cases", {})),
        trailing_stem_label_pattern=build_trailing_stem_label_pattern(
            trailing_stem_labels
        ),
    )


def load_sanitize_cases(config_path: Path | None = None) -> SanitizeCases:
    del config_path  # Backward-compatible signature; cases are loaded from 4 files.
    core_mappings_data = _load_toml(CORE_MAPPINGS_CASES_PATH)
    idempotency_data = _load_toml(IDEMPOTENCY_CASES_PATH)
    rule_trace_data = _load_toml(RULE_TRACE_CASES_PATH)
    directory_cases_data = _load_toml(DIRECTORY_CASES_PATH)

    core_mappings_raw = core_mappings_data.get("core_mappings", [])
    idempotency_raw = idempotency_data.get("idempotency", {}).get("raw_stems", [])
    rule_trace_raw = rule_trace_data.get("rule_trace", [])
    directory_cases_raw = directory_cases_data.get("directory_cases", [])

    if not isinstance(core_mappings_raw, list):
        raise ValueError("`core_mappings` must be an array of tables.")
    if not isinstance(idempotency_raw, list):
        raise ValueError("`idempotency.raw_stems` must be a list.")
    if not isinstance(rule_trace_raw, list):
        raise ValueError("`rule_trace` must be an array of tables.")
    if not isinstance(directory_cases_raw, list):
        raise ValueError("`directory_cases` must be an array of tables.")

    if VENDOR_CASES_DIR.exists():
        for vendor_path in sorted(VENDOR_CASES_DIR.glob("*.toml")):
            vendor_data = _load_toml(vendor_path)
            vendor_core_mappings = vendor_data.get("core_mappings", [])
            vendor_rule_trace = vendor_data.get("rule_trace", [])
            if not isinstance(vendor_core_mappings, list):
                raise ValueError(
                    f"`core_mappings` in {vendor_path} must be an array of tables."
                )
            if not isinstance(vendor_rule_trace, list):
                raise ValueError(
                    f"`rule_trace` in {vendor_path} must be an array of tables."
                )
            core_mappings_raw.extend(vendor_core_mappings)
            rule_trace_raw.extend(vendor_rule_trace)

    return SanitizeCases(
        core_mappings=[_to_core_mapping_case(item) for item in core_mappings_raw],
        idempotency_raw_stems=[str(item) for item in idempotency_raw],
        rule_trace=[_to_rule_trace_case(item) for item in rule_trace_raw],
        directory_cases=[_to_directory_case(item) for item in directory_cases_raw],
    )
