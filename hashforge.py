#!/usr/bin/env python3
"""HashForge - Defensive Security Laboratory Candidate Dataset & Password Profiling Suite.

Derived from HashForge (Common User Passwords Profiler) with modernized architecture,
Hashcat mutation rule engine, search-space estimation, and streaming I/O.
"""

import argparse
import json
import os
import sys

from hashforge.config import load_config
from hashforge.profile.models import Profile
from hashforge.hashcat.discovery import discover_rule_files, format_rules_table
from hashforge.pipeline import run_hashforge_pipeline

__version__ = "4.0.0-hashforge"


def print_banner() -> None:
    banner = r"""
  _    _           _     ______                 
 | |  | |         | |   |  ____|                
 | |__| | __ _ ___| |__ | |__ ___  _ __ __ _  ___ 
 |  __  |/ _` / __| '_ \|  __/ _ \| '__/ _` |/ _ \
 | |  | | (_| \__ \ | | | | | (_) | | | (_| |  __/
 |_|  |_|\__,_|___/_| |_|_|  \___/|_|  \__, |\___|
                                        __/ |     
   Defensive Laboratory Password Profiler|___/     v""" + __version__
    print(banner)
    print("=" * 70)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hashforge",
        description="HashForge: Defensive Laboratory Profile-Based Candidate Dataset Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive terminal wizard (primary UX):
    python hashforge.py

  Direct transformation with dry-run estimation:
    python hashforge.py --rule best66.rule --dry-run

  Batch generation from synthetic profile JSON:
    python hashforge.py --profile test_profile.json -r top10_2025.rule -o output/test.txt

  Discover available rule transformations:
    python hashforge.py --list-rules
        """,
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        default=False,
        help="Run interactive profile wizard (default when no profile file provided)",
    )
    parser.add_argument(
        "-p", "--profile",
        metavar="FILE",
        help="Path to JSON file containing synthetic profile data",
    )
    parser.add_argument(
        "-r", "--rule",
        metavar="RULE",
        help="Transformation rule filename or path (e.g. best66.rule)",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="Discover and display available transformation profiles under rules/ directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry-run: calculate base candidate count and estimate search-space without writing output",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        default=os.path.join("output", "hashforge_wordlist.txt"),
        help="Destination path for resulting UTF-8 wordlist (default: output/hashforge_wordlist.txt)",
    )
    parser.add_argument(
        "--rules-dir",
        metavar="DIR",
        default="rules",
        help="Directory containing Hashcat transformation .rule files (default: rules)",
    )
    parser.add_argument(
        "--min-len",
        type=int,
        metavar="N",
        help="Minimum candidate word length filter",
    )
    parser.add_argument(
        "--max-len",
        type=int,
        metavar="N",
        help="Maximum candidate word length filter",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        metavar="N",
        default=500000,
        help="Hard safety bound on maximum unique candidates to generate (default: 500,000)",
    )
    parser.add_argument(
        "-c", "--config",
        metavar="FILE",
        default="hashforge.cfg",
        help="Configuration file (default: hashforge.cfg)",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode: suppress startup banner",
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show program version and exit",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        print(f"HashForge {__version__} (HashForge Modernized Engine)")
        sys.exit(0)

    if not args.quiet:
        print_banner()

    config = load_config(args.config)

    if args.list_rules:
        rules_found = discover_rule_files(args.rules_dir)
        print(format_rules_table(rules_found))
        sys.exit(0)

    # Load profile if JSON specified
    profile_obj = None
    if args.profile:
        if not os.path.isfile(args.profile):
            print(f"[-] Profile file not found: {args.profile}")
            sys.exit(1)
        with open(args.profile, "r", encoding="utf-8") as pf:
            profile_data = json.load(pf)
        profile_obj = Profile.from_dict(profile_data)

    # Run the HashForge pipeline
    try:
        run_hashforge_pipeline(
            profile=profile_obj,
            rule_path=args.rule,
            output_path=args.output,
            rules_dir=args.rules_dir,
            dry_run=args.dry_run,
            min_len=args.min_len,
            max_len=args.max_len,
            max_candidates=args.max_candidates,
            interactive=(profile_obj is None),
            config=config,
        )
    except KeyboardInterrupt:
        print("\n[-] Operation cancelled by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()
