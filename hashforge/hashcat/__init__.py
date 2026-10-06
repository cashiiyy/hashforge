"""Hashcat integration package for HashForge."""

from .discovery import (
    RuleMetadata,
    discover_rule_files,
    format_rules_table,
    inspect_rule_file,
    prompt_select_rule,
    format_size,
)
from .estimator import EstimationReport, estimate_search_space

__all__ = [
    "RuleMetadata",
    "discover_rule_files",
    "format_rules_table",
    "inspect_rule_file",
    "prompt_select_rule",
    "format_size",
    "EstimationReport",
    "estimate_search_space",
]
