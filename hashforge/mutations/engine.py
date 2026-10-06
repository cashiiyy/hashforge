"""Bounded transformation engine for streaming candidate generation."""

from typing import Iterable, List, Optional, Iterator, Set
from .rules import HashcatRule


def transform_candidates_stream(
    base_candidates: Iterable[str],
    rules: Optional[List[HashcatRule]] = None,
    min_len: int = 3,
    max_len: int = 32,
    max_candidates: int = 500000,
) -> Iterator[str]:
    """Stream transformed candidates with deduplication, length filtering, and hard upper limit.

    Guarantees:
    - Never creates unbounded output: stops strictly at max_candidates.
    - Memory bounded: seen set never exceeds max_candidates entries.
    - Generates candidates on-demand via streaming generator.
    """
    seen: Set[str] = set()
    count = 0

    # Ensure rules list
    active_rules = rules if (rules and len(rules) > 0) else []

    # Yield valid base candidates first
    for candidate in base_candidates:
        cand_str = str(candidate).strip()
        if not cand_str:
            continue
        if min_len <= len(cand_str) <= max_len:
            if cand_str not in seen:
                seen.add(cand_str)
                yield cand_str
                count += 1
                if count >= max_candidates:
                    return

    # If no transformation rules selected, we are done
    if not active_rules:
        return

    # Apply rules across candidates
    for base_word in base_candidates:
        word_str = str(base_word).strip()
        if not word_str:
            continue

        for rule in active_rules:
            try:
                transformed = rule.apply(word_str)
            except Exception:
                continue

            if transformed is None:
                continue

            if min_len <= len(transformed) <= max_len:
                if transformed not in seen:
                    seen.add(transformed)
                    yield transformed
                    count += 1
                    if count >= max_candidates:
                        return
