"""Main orchestration pipeline for HashForge."""

import os
import time
import sys
import threading
from typing import Optional, Dict, Any, List
from .config import AppConfig, load_config
from .profile.models import Profile
from .profile.wizard import run_profile_wizard, _safe_input, _ask_yes_no
from .generators.combinations import generate_base_candidates
from .hashcat.discovery import discover_rule_files, RuleMetadata
from .hashcat.estimator import estimate_search_space
from .mutations.rules import load_rule_file, HashcatRule
from .mutations.engine import transform_candidates_stream
from .output.writer import stream_candidates_to_file

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


class Spinner:
    def __init__(self, message="Loading..."):
        self.spinner_chars = "|/-\\"
        self.message = message
        self.running = False
        self.thread = None

    def spin(self):
        idx = 0
        while self.running:
            sys.stdout.write(f"\r{CYAN}{self.spinner_chars[idx]} {self.message}{RESET}")
            sys.stdout.flush()
            idx = (idx + 1) % len(self.spinner_chars)
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 4) + "\r")

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

def format_rules_menu(rules_found: List[RuleMetadata]) -> str:
    """Format the discovered rules into a selectable menu."""
    if not rules_found:
        return f"{RED}No rule files found.{RESET}"
    lines = [f"\n{BOLD}{CYAN}AVAILABLE RULES{RESET}\n{CYAN}==============={RESET}\n"]
    for i, meta in enumerate(rules_found, start=1):
        lines.append(f"{YELLOW}[{i}]{RESET} {meta.name}")
    return "\n".join(lines)


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
    if config is None:
        config = load_config()

    eff_min_len = min_len if min_len is not None else config.wcfrom
    eff_max_len = max_len if max_len is not None else config.wcto
    eff_max_candidates = max_candidates if max_candidates is not None else config.max_candidates
    eff_output_path = output_path if output_path else config.default_output_file

    if profile is None:
        profile = run_profile_wizard(show_banner=True)

    print(f"\n{CYAN}Generating base candidates...{RESET}")
    spinner = Spinner("Building base profile combinations...")
    spinner.start()
    base_candidates = generate_base_candidates(
        profile,
        config=config,
        min_len=1,
        max_len=100,
        max_candidates=10000000,
    )
    spinner.stop()
    print(f"\n{GREEN}[+] Base candidates generated: {len(base_candidates):,}{RESET}")

    selected_rule_path = rule_path
    selected_rule_name = "None"
    loaded_rules: List[HashcatRule] = []

    if interactive and not skip_transformation_prompt and not selected_rule_path:
        print(f"\n{BOLD}Would you like to apply a Hashcat rule?{RESET}")
        print(f"\n{YELLOW}[Y]{RESET} Yes\n{YELLOW}[N]{RESET} No\n{YELLOW}[ENTER]{RESET} No\n")
        add_rule = _safe_input("> ").strip().lower()
        
        if add_rule in ("y", "yes"):
            while True:
                rules_found = discover_rule_files(rules_dir)
                print(format_rules_menu(rules_found))
                print(f"\nSelect a rule or press {YELLOW}ENTER{RESET} for none:\n")
                choice = _safe_input("> ").strip()
                if not choice:
                    print(f"\n{GREEN}[+] Rule processing skipped.{RESET}")
                    break
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(rules_found):
                        chosen_meta = rules_found[idx]
                        selected_rule_path = chosen_meta.path
                        selected_rule_name = chosen_meta.name
                        
                        spinner = Spinner(f"Loading rules from {selected_rule_name}...")
                        spinner.start()
                        loaded_rules = load_rule_file(selected_rule_path)
                        spinner.stop()
                        
                        print(f"\n{BOLD}Selected:{RESET}\n{CYAN}{selected_rule_name}{RESET}\n\n{BOLD}Rules:{RESET}\n{len(loaded_rules):,}\n")
                        
                        if _ask_yes_no("Proceed?", default=True):
                            break
                        else:
                            selected_rule_path = None
                            loaded_rules = []
                            continue
                    else:
                        print(f"{RED}[-] Invalid selection.{RESET}")
                except ValueError:
                    print(f"{RED}[-] Invalid selection.{RESET}")
        else:
            print(f"\n{GREEN}[+] Rule processing skipped.{RESET}")

    elif selected_rule_path:
        if not os.path.isfile(selected_rule_path) and os.path.isfile(os.path.join(rules_dir, selected_rule_path)):
            selected_rule_path = os.path.join(rules_dir, selected_rule_path)

        if os.path.isfile(selected_rule_path):
            try:
                loaded_rules = load_rule_file(selected_rule_path)
                selected_rule_name = os.path.basename(selected_rule_path)
            except Exception as e:
                print(f"{RED}[-] Error loading rule file {selected_rule_path}: {e}{RESET}")
                loaded_rules = []

    estimated_total = max(len(base_candidates) * len(loaded_rules) if loaded_rules else len(base_candidates), len(base_candidates))
    
    if estimated_total > eff_max_candidates:
        print(f"\n{RED}WARNING: The selected configuration may generate more than {eff_max_candidates:,} candidates.{RESET}")
        print(f"{YELLOW}[1]{RESET} Reduce rule count\n{YELLOW}[2]{RESET} Continue anyway\n{YELLOW}[3]{RESET} Cancel\n")
        resp = _safe_input("> ").strip()
        if resp == "1":
            limit = _safe_input("Enter maximum number of rules: ").strip()
            if limit.isdigit():
                loaded_rules = loaded_rules[:int(limit)]
                estimated_total = len(base_candidates) * len(loaded_rules)
        elif resp == "3":
            return {"count": 0, "output_path": eff_output_path}

    if interactive:
        print(f"\n{BOLD}{CYAN}WORDLIST SETTINGS{RESET}")
        print(f"{CYAN}================={RESET}\n")
        min_in = _safe_input(f"Minimum length [{eff_min_len}]: ")
        if min_in.isdigit(): eff_min_len = int(min_in)
        
        max_in = _safe_input(f"Maximum length [{eff_max_len}]: ")
        if max_in.isdigit(): eff_max_len = int(max_in)
        
        out_in = _safe_input(f"Output filename [{eff_output_path}]: ")
        if out_in: eff_output_path = out_in
        if not eff_output_path.endswith(".txt"): eff_output_path += ".txt"

    if dry_run:
        return {"count": 0, "output_path": eff_output_path}

    # Generate Estimates
    avg_len = 10
    estimated_size_bytes = estimated_total * (avg_len + 1)
    estimated_size_mb = estimated_size_bytes / (1024 * 1024)
    write_speed_est = 250000  # lines per second approx
    estimated_time_sec = estimated_total / write_speed_est

    print(f"\n{BOLD}ESTIMATION{RESET}")
    print(f"==========")
    print(f"Candidates    : ~{estimated_total:,}")
    print(f"Size on Disk  : ~{estimated_size_mb:.2f} MB")
    print(f"Time          : ~{estimated_time_sec:.2f} seconds\n")

    print(f"{BOLD}{CYAN}GENERATING{RESET}")
    print(f"{CYAN}=========={RESET}\n")

    candidate_stream = transform_candidates_stream(
        base_candidates=base_candidates,
        rules=loaded_rules,
        min_len=eff_min_len,
        max_len=eff_max_len,
        max_candidates=eff_max_candidates,
    )

    start_time = time.time()
    spinner = Spinner("Writing wordlist to disk...")
    spinner.start()
    
    def progress_callback(current_count: int) -> None:
        pass # Using simple spinner instead

    result = stream_candidates_to_file(
        candidate_stream=candidate_stream,
        output_path=eff_output_path,
        on_progress=progress_callback,
    )
    
    spinner.stop()
    duration = time.time() - start_time

    print(f"\n{BOLD}{GREEN}COMPLETE{RESET}")
    print(f"{GREEN}========{RESET}")
    print(f"\n{BOLD}Output:{RESET}\n{result['output_path']}")
    print(f"\n{BOLD}Unique candidates:{RESET}\n{result['count']:,}")
    print(f"\n{BOLD}File size:{RESET}\n{result['size_formatted']}")
    print(f"\n{BOLD}Generation time:{RESET}\n{duration:.2f} seconds")

    return result
