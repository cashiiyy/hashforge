"""Base candidate generation logic for HashForge."""

from typing import List, Set, Iterable, Optional
from ..profile.models import Profile
from ..config import AppConfig


def make_leet(word: str, leet_map: dict) -> str:
    """Transform word using leet speak substitution table."""
    res = word
    for char, leet_char in leet_map.items():
        res = res.replace(char, leet_char)
    return res


import itertools


def extract_date_parts(date_str: str) -> List[str]:
    """Extract standard date components and combinations from DDMMYYYY string."""
    if not date_str or len(date_str) != 8 or not date_str.isdigit():
        return []

    dd = date_str[:2]
    mm = date_str[2:4]
    yyyy = date_str[4:]
    yy = date_str[6:]
    yyy = date_str[5:]
    xd = date_str[1:2]
    xm = date_str[3:4]

    bds = [yy, yyy, yyyy, xd, xm, dd, mm]
    parts: List[str] = [date_str]

    for r in (1, 2, 3):
        for p in itertools.permutations(bds, r):
            comb = "".join(p)
            if comb:
                parts.append(comb)

    # Deduplicate preserving order
    return list(dict.fromkeys(parts))


def generate_base_candidates(
    profile: Profile,
    config: Optional[AppConfig] = None,
    min_len: Optional[int] = None,
    max_len: Optional[int] = None,
    max_candidates: int = 100000,
) -> List[str]:
    """Generate bounded, deduplicated base candidate dataset from a synthetic Profile."""
    if config is None:
        config = AppConfig()

    eff_min_len = min_len if min_len is not None else config.wcfrom
    eff_max_len = max_len if max_len is not None else config.wcto

    # 1. Base tokens
    raw_tokens = [
        profile.name,
        profile.surname,
        profile.nick,
        profile.wife,
        profile.wifen,
        profile.kid,
        profile.kidn,
        profile.pet,
        profile.company,
    ]
    raw_tokens.extend(profile.words)
    base_words = [w.strip().lower() for w in raw_tokens if w and w.strip()]

    if not base_words:
        return []

    # Title-case and upper-case variants
    expanded_words = []
    for w in base_words:
        expanded_words.append(w)
        expanded_words.append(w.title())
        expanded_words.append(w.upper())
    expanded_words = list(dict.fromkeys(expanded_words))

    # Reversals
    reversed_words = [w[::-1] for w in base_words if len(w) > 1]
    reversed_words = list(dict.fromkeys(reversed_words))

    # Date components
    bd_parts = extract_date_parts(profile.birthdate)
    partner_bd_parts = extract_date_parts(profile.wifeb)
    kid_bd_parts = extract_date_parts(profile.kidb)
    all_dates = list(dict.fromkeys(bd_parts + partner_bd_parts + kid_bd_parts + config.years))

    # Special characters
    special_chars = []
    if profile.spechars1 and config.chars:
        for c1 in config.chars:
            special_chars.append(c1)
            for c2 in config.chars:
                special_chars.append(c1 + c2)

    # 2. Candidate collection with deterministic bounded set
    seen: Set[str] = set()
    candidates: List[str] = []

    def add_cand(cand: str) -> bool:
        if not cand:
            return False
        if len(cand) < eff_min_len or len(cand) > eff_max_len:
            return False
        if cand not in seen:
            seen.add(cand)
            candidates.append(cand)
            return len(candidates) >= max_candidates
        return False

    # A. Add individual words and date strings
    for w in expanded_words + reversed_words:
        if add_cand(w):
            return candidates

    for d in all_dates:
        if add_cand(d):
            return candidates

    # B. Word + Word combinations (e.g. name + surname, surname + name, nick + pet)
    for w1 in expanded_words:
        for w2 in expanded_words:
            if w1.lower() != w2.lower():
                if add_cand(w1 + w2):
                    return candidates
                if add_cand(w1 + "_" + w2):
                    return candidates
                if add_cand(w1 + "." + w2):
                    return candidates

    # C. Word + Date / Year combinations
    for w in expanded_words + reversed_words:
        for d in all_dates:
            if add_cand(w + d):
                return candidates
            if add_cand(d + w):
                return candidates
            if add_cand(w + "_" + d):
                return candidates
            if add_cand(w + "." + d):
                return candidates

    # D. Random number suffixes (numfrom to numto)
    if profile.randnum:
        num_start = max(0, config.numfrom)
        num_end = min(101, config.numto + 1)
        for w in expanded_words:
            for n in range(num_start, num_end):
                if add_cand(f"{w}{n}"):
                    return candidates
                if add_cand(f"{w}_{n}"):
                    return candidates

    # E. Special characters additions
    if profile.spechars1 and special_chars:
        for w in expanded_words:
            for sc in special_chars:
                if add_cand(w + sc):
                    return candidates
                if add_cand(sc + w):
                    return candidates

    # F. Leet mode transformations
    if profile.leetmode:
        current_snapshot = list(candidates)
        for c in current_snapshot:
            leet_cand = make_leet(c.lower(), config.leet)
            if add_cand(leet_cand):
                return candidates

    return candidates
