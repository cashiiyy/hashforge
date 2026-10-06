"""Main orchestration pipeline for HashForge."""

import os
from typing import Optional, Dict, Any, List
from .config import AppConfig, load_config
from .profile.models import Profile
from .profile.wizard import run_profile_wizard, _ask_yes_no
from .generators.combinations import generate_base_candidates
from .hashcat.discovery import discover_rule_files, prompt_select_rule, RuleMetadata
from .hashcat.estimator import estimate_search_space
from .mutations.rules import load_rule_file, HashcatRule
from .mutations.engine import transform_candidates_stream
from .output.writer import stream_candidates_to_file


def run_hashforge_pipeline(
    profile: Optional[Profile] = None,
    rule_path: Optional[str] = None,
    output_path: Optional[str] = None,
    rules_dir: str = "rules",
    dry_run: bool = False,
    min_len: Optional[int] = None,
    max_len: Optional[int] = None,
    max_candidates: Optional[int] = None,
    interactive: bool = True,
    config: Optional[AppConfig] = None,
    skip_transformation_prompt: bool = False,
) -> Dict[str, Any]:
    """Execute the complete HashForge workflow:
    1. Collect Profile (interactive wizard or provided profile)
    2. Base Candidate Generation
    3. Transformation Selection (Ask -> Discover -> Display -> Select)
    4. Search Space Estimation & Dry-Run
    5. Bounded Transformation
    6. Streaming UTF-8 TXT Output
    """
    if config is None:
        config = load_config()

    eff_min_len = min_len if min_len is not None else config.wcfrom
    eff_max_len = max_len if max_len is not None else config.wcto
    eff_max_candidates = max_candidates if max_candidates is not None else config.max_candidates
    eff_output_path = output_path if output_path else config.default_output_file

    # 1. Profile questions / collection
    if profile is None:
        profile = run_profile_wizard(show_banner=True)

    # 2. Base candidate generation
    print("\n[+] Generating base candidate dataset from synthetic profile...")
    base_candidates = generate_base_candidates(
        profile,
        config=config,
        min_len=eff_min_len,
        max_len=eff_max_len,
        max_candidates=eff_max_candidates,
    )
    print(f"[+] Generated {len(base_candidates):,} deduplicated base candidates.")

    if not base_candidates:
        print("[-] No base candidates generated with current length and profile settings.")
        return {"count": 0, "output_path": eff_output_path, "base_count": 0}

    # 3. Transformation selection
    selected_rule_path = rule_path
    selected_rule_name = "None (Base Profile Only)"
    loaded_rules: List[HashcatRule] = []

    if not selected_rule_path and interactive and not skip_transformation_prompt:
        # Prompt: Add a transformation profile? [y/N]
        add_trans = _ask_yes_no("\n> Add a transformation profile?")
        if add_trans:
            rules_found = discover_rule_files(rules_dir)
            chosen_meta = prompt_select_rule(rules_found)
            if chosen_meta:
                selected_rule_path = chosen_meta.path
                selected_rule_name = chosen_meta.name

    if selected_rule_path:
        if not os.path.isfile(selected_rule_path) and os.path.isfile(os.path.join(rules_dir, selected_rule_path)):
            selected_rule_path = os.path.join(rules_dir, selected_rule_path)

        if os.path.isfile(selected_rule_path):
            try:
                loaded_rules = load_rule_file(selected_rule_path)
                selected_rule_name = os.path.basename(selected_rule_path)
                print(f"[+] Loaded {len(loaded_rules):,} mutation rules from '{selected_rule_name}'.")
            except Exception as e:
                print(f"[-] Error loading rule file {selected_rule_path}: {e}")
                loaded_rules = []
        else:
            print(f"[-] Rule file not found: {selected_rule_path}. Proceeding with base candidates.")

    # 4. Search-space estimation & dry-run
    report = estimate_search_space(
        base_count=len(base_candidates),
        rule_count=len(loaded_rules),
        rule_name=selected_rule_name,
        min_len=eff_min_len,
        max_len=eff_max_len,
        max_candidates=eff_max_candidates,
    )
    print(report.summary())

    if dry_run:
        print("[*] Dry-run enabled: skipping file generation.")
        return {
            "count": 0,
            "output_path": eff_output_path,
            "dry_run": True,
            "base_count": len(base_candidates),
            "report": report,
        }

    # 5. Bounded transformation & Streaming Output
    print(f"[+] Streaming candidate dataset to: {eff_output_path}")

    candidate_stream = transform_candidates_stream(
        base_candidates=base_candidates,
        rules=loaded_rules,
        min_len=eff_min_len,
        max_len=eff_max_len,
        max_candidates=eff_max_candidates,
    )

    def progress_callback(current_count: int) -> None:
        print(f"    ... {current_count:,} candidates written ...")

    result = stream_candidates_to_file(
        candidate_stream=candidate_stream,
        output_path=eff_output_path,
        on_progress=progress_callback,
    )

    print(f"\n[+] Successfully generated wordlist!")
    print(f"    File       : {result['output_path']}")
    print(f"    Candidates : {result['count']:,}")
    print(f"    Size       : {result['size_formatted']}")
    print(f"    Encoding   : UTF-8\n")

    result["base_count"] = len(base_candidates)
    result["rule_count"] = len(loaded_rules)
    result["report"] = report

    return result
