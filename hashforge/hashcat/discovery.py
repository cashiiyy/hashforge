"""Discovery and inspection of Hashcat transformation rule files."""

import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RuleMetadata:
    index: int
    name: str
    path: str
    size_bytes: int
    size_formatted: str
    rule_count: int
    complexity: str
    description: str


def format_size(bytes_num: int) -> str:
    """Format bytes into human-readable size string."""
    if bytes_num < 1024:
        return f"{bytes_num} B"
    elif bytes_num < 1024 * 1024:
        return f"{bytes_num / 1024:.1f} KB"
    else:
        return f"{bytes_num / (1024 * 1024):.1f} MB"


def inspect_rule_file(path: str, index: int = 1) -> RuleMetadata:
    """Safely inspect a .rule file without executing it."""
    name = os.path.basename(path)
    size_bytes = os.path.getsize(path)
    size_str = format_size(size_bytes)

    rule_count = 0
    desc_lines = []

    # Read top lines for description and count total rules
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for idx, line in enumerate(f):
                line_str = line.strip()
                if not line_str:
                    continue
                if line_str.startswith("#"):
                    # Collect header comments as description
                    clean_comment = line_str.lstrip("#").strip()
                    if clean_comment and len(desc_lines) < 2:
                        desc_lines.append(clean_comment)
                else:
                    rule_count += 1
    except Exception:
        # Fallback reading
        try:
            with open(path, "r", encoding="latin-1", errors="replace") as f:
                for line in f:
                    line_str = line.strip()
                    if line_str and not line_str.startswith("#"):
                        rule_count += 1
        except Exception:
            pass

    # Determine complexity tier
    if rule_count <= 100:
        complexity = "Lightweight"
    elif rule_count <= 1000:
        complexity = "Medium"
    elif rule_count <= 10000:
        complexity = "Extensive"
    else:
        complexity = "Massive"

    description = " | ".join(desc_lines) if desc_lines else "Standard transformation rules"
    # Sanitize characters to printable ASCII to prevent encoding errors on standard Windows terminal consoles
    description = "".join(c if (32 <= ord(c) <= 126) else " " for c in description).strip()
    if len(description) > 45:
        description = description[:42] + "..."

    return RuleMetadata(
        index=index,
        name=name,
        path=path,
        size_bytes=size_bytes,
        size_formatted=size_str,
        rule_count=rule_count,
        complexity=complexity,
        description=description,
    )


def discover_rule_files(rules_dir: str = "rules") -> List[RuleMetadata]:
    """Discover and safely inspect all rule files in rules directory."""
    if not os.path.isdir(rules_dir):
        # Look in workspace root if relative path
        alt_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), rules_dir)
        if os.path.isdir(alt_dir):
            rules_dir = alt_dir
        else:
            return []

    discovered: List[RuleMetadata] = []
    idx = 1

    # Traverse directory (including subdirectories like rules/hybrid)
    for root, _, files in os.walk(rules_dir):
        for file in sorted(files):
            if file.endswith(".rule"):
                full_path = os.path.join(root, file)
                rel_name = os.path.relpath(full_path, rules_dir).replace("\\", "/")
                meta = inspect_rule_file(full_path, index=idx)
                meta.name = rel_name
                discovered.append(meta)
                idx += 1

    return discovered


def format_rules_table(rules: List[RuleMetadata]) -> str:
    """Format discovered rules into a neat terminal table."""
    if not rules:
        return "[-] No transformation profiles (.rule) found in rules/ directory.\n"

    lines = []
    lines.append("=" * 95)
    lines.append(f" {'#':>3}  {'Filename':<35}  {'Size':>9}  {'Rules':>7}  {'Complexity':<12}  {'Description'}")
    lines.append("-" * 95)

    for r in rules:
        lines.append(
            f" [{r.index:>2}]  {r.name:<35}  {r.size_formatted:>9}  {r.rule_count:>7}  {r.complexity:<12}  {r.description}"
        )

    lines.append("=" * 95)
    return "\n".join(lines)


def prompt_select_rule(rules: List[RuleMetadata]) -> Optional[RuleMetadata]:
    """Interactive prompt to let user select one rule profile, or press ENTER for none."""
    if not rules:
        return None

    print(format_rules_table(rules))
    print("[*] Select a transformation profile by number or filename.")
    print("[*] Press ENTER for none (continue with base profile only).\n")

    try:
        choice = input("> Select profile [ENTER for none]: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None

    if not choice:
        return None

    # Check numeric index
    if choice.isdigit():
        num = int(choice)
        for r in rules:
            if r.index == num:
                return r

    # Check filename match
    choice_lower = choice.lower()
    for r in rules:
        if r.name.lower() == choice_lower or r.name.lower().endswith("/" + choice_lower):
            return r
        # Partial match without .rule
        if r.name.lower() == choice_lower + ".rule":
            return r

    print(f"[-] Profile '{choice}' not recognized. Proceeding without transformation profile.")
    return None
