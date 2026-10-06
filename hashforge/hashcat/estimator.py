"""Search-space estimation and dry-run reporting for HashForge."""

from dataclasses import dataclass
from typing import Optional
from .discovery import format_size


@dataclass
class EstimationReport:
    base_count: int
    rule_name: str
    rule_count: int
    multiplier: int
    theoretical_total: int
    bounded_total: int
    min_len: int
    max_len: int
    max_candidates: int
    estimated_size_bytes: int
    estimated_size_formatted: str
    is_truncated: bool

    def summary(self) -> str:
        """Return formatted string summary of the estimation."""
        lines = [
            "\n" + "=" * 65,
            "         HashForge Search-Space Estimation & Dry-Run",
            "=" * 65,
            f"  Base Profile Candidates    : {self.base_count:,}",
            f"  Selected Rule Profile      : {self.rule_name}",
            f"  Active Mutation Rules      : {self.rule_count:,}",
            f"  Search Space Multiplier    : {self.multiplier}x",
            "-" * 65,
            f"  Theoretical Combinations   : {self.theoretical_total:,}",
            f"  Safety Candidate Bound     : {self.max_candidates:,}",
            f"  Candidate Length Window    : {self.min_len} to {self.max_len} chars",
            f"  Effective Candidate Limit  : {self.bounded_total:,}",
            f"  Estimated Output Size      : ~{self.estimated_size_formatted}",
        ]
        if self.is_truncated:
            lines.append(
                f"\n  [!] NOTICE: Output bounded by limit ({self.max_candidates:,})."
                f"\n      {self.theoretical_total - self.bounded_total:,} combinations will be pruned to prevent unbounded memory/disk usage."
            )
        lines.append("=" * 65 + "\n")
        return "\n".join(lines)


def estimate_search_space(
    base_count: int,
    rule_count: int = 0,
    rule_name: str = "None (Base Profile Only)",
    min_len: int = 3,
    max_len: int = 32,
    max_candidates: int = 500000,
    avg_word_len: int = 10,
) -> EstimationReport:
    """Calculate search space metrics and bounded limits."""
    multiplier = max(1, rule_count) if rule_count > 0 else 1
    theoretical_total = base_count if rule_count == 0 else base_count + (base_count * rule_count)
    bounded_total = min(theoretical_total, max_candidates)

    # Estimate output size (average candidate length + 1 newline byte)
    est_bytes = bounded_total * (avg_word_len + 1)
    est_size_str = format_size(est_bytes)

    is_truncated = theoretical_total > max_candidates

    return EstimationReport(
        base_count=base_count,
        rule_name=rule_name,
        rule_count=rule_count,
        multiplier=multiplier,
        theoretical_total=theoretical_total,
        bounded_total=bounded_total,
        min_len=min_len,
        max_len=max_len,
        max_candidates=max_candidates,
        estimated_size_bytes=est_bytes,
        estimated_size_formatted=est_size_str,
        is_truncated=is_truncated,
    )
