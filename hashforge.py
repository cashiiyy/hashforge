#!/usr/bin/env python3
import argparse
import json
import os
import sys

from hashforge.config import load_config
from hashforge.profile.models import Profile
from hashforge.hashcat.discovery import discover_rule_files, format_rules_table
from hashforge.pipeline import run_hashforge_pipeline
from hashforge.profile.wizard import run_profile_wizard

__version__ = "4.0.0-hashforge"

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_banner() -> None:
    banner = f"""{CYAN}
╔══════════════════════════════════════╗
║             {BOLD}HASHFORGE{RESET}{CYAN}                ║
║ Profile-Driven Wordlist Generator    ║
╚══════════════════════════════════════╝{RESET}"""
    print(banner)


def interactive_main():
    print_banner()
    print(f"\n{YELLOW}[1]{RESET} Build profile\n{YELLOW}[2]{RESET} Load profile\n{YELLOW}[3]{RESET} Exit\n")
    try:
        choice = input(f"{YELLOW}>{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)
        
    profile_obj = None
    if choice == "1":
        profile_obj = run_profile_wizard()
    elif choice == "2":
        path = input(f"Enter profile JSON path: ").strip()
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                profile_obj = Profile.from_dict(json.load(f))
        else:
            print(f"{RED}File not found.{RESET}")
            sys.exit(1)
    else:
        sys.exit(0)
        
    run_hashforge_pipeline(
        profile=profile_obj,
        rule_path=None,
        output_path=os.path.join("output", "hashforge_wordlist.txt"),
        rules_dir="rules",
        dry_run=False,
        min_len=None,
        max_len=None,
        max_candidates=10000000,
        interactive=True,
        config=load_config("hashforge.cfg"),
    )

def main() -> None:
    # Initialize ANSI escape sequences on Windows
    os.system("")
    
    if len(sys.argv) == 1:
        interactive_main()
    else:
        parser = argparse.ArgumentParser(prog="hashforge")
        parser.add_argument("-i", "--interactive", action="store_true", default=False)
        parser.add_argument("-p", "--profile", metavar="FILE")
        parser.add_argument("-r", "--rule", metavar="RULE")
        parser.add_argument("--list-rules", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("-o", "--output", default=os.path.join("output", "hashforge_wordlist.txt"))
        parser.add_argument("--rules-dir", default="rules")
        parser.add_argument("--min-len", type=int)
        parser.add_argument("--max-len", type=int)
        parser.add_argument("--max-candidates", type=int, default=10000000)
        parser.add_argument("-c", "--config", default="hashforge.cfg")
        parser.add_argument("-q", "--quiet", action="store_true")
        args = parser.parse_args()
        
        if args.list_rules:
            rules_found = discover_rule_files(args.rules_dir)
            print(format_rules_table(rules_found))
            sys.exit(0)

        profile_obj = None
        if args.profile:
            with open(args.profile, "r", encoding="utf-8") as pf:
                profile_obj = Profile.from_dict(json.load(pf))

        if args.interactive or profile_obj is None:
            interactive_main()
            return

        run_hashforge_pipeline(
            profile=profile_obj,
            rule_path=args.rule,
            output_path=args.output,
            rules_dir=args.rules_dir,
            dry_run=args.dry_run,
            min_len=args.min_len,
            max_len=args.max_len,
            max_candidates=args.max_candidates,
            interactive=False,
            config=load_config(args.config),
        )

if __name__ == "__main__":
    main()
