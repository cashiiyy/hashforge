import os

WIZARD_PY = """\"\"\"Interactive terminal profile wizard for HashForge.\"\"\"

import sys
from typing import Optional
from .models import Profile

def _safe_input(prompt: str, default: str = "") -> str:
    try:
        val = input(prompt)
        return val.strip()
    except (EOFError, KeyboardInterrupt):
        return default

def _ask_yes_no(prompt: str, default: bool = False) -> bool:
    default_str = "Y/n" if default else "y/N"
    full_prompt = f"{prompt} [{default_str}]: "
    ans = _safe_input(full_prompt).lower()
    if not ans:
        return default
    return ans in ("y", "yes", "1", "true")

def run_profile_wizard(show_banner: bool = True) -> Profile:
    print("\\nTARGET PROFILE")
    print("==============")

    first_name = _safe_input("First name: ")
    last_name = _safe_input("Last name: ")
    nickname = _safe_input("Nickname: ")
    username = _safe_input("Username: ")
    print("")
    partner_name = _safe_input("Partner name: ")
    partner_nickname = _safe_input("Partner nickname: ")
    print("")
    child_name = _safe_input("Child name: ")
    pet_name = _safe_input("Pet name: ")
    print("")
    company = _safe_input("Company: ")
    org = _safe_input("Organization: ")
    school = _safe_input("School: ")
    college = _safe_input("College: ")
    print("")
    city = _safe_input("City: ")
    country = _safe_input("Country: ")
    location = _safe_input("Location: ")
    print("")
    ssid = _safe_input("SSID: ")
    print("")
    sports = _safe_input("Favorite sports: ")
    teams = _safe_input("Favorite teams: ")
    print("")
    games = _safe_input("Favorite games: ")
    movies = _safe_input("Favorite movies: ")
    shows = _safe_input("Favorite shows: ")
    music = _safe_input("Favorite music/artists: ")
    print("")
    hobbies = _safe_input("Hobbies: ")
    tech = _safe_input("Technologies: ")
    lang = _safe_input("Programming languages: ")
    print("")
    projects = _safe_input("Projects: ")
    brands = _safe_input("Brands: ")
    products = _safe_input("Products: ")
    print("")
    dates = _safe_input("Important dates: ")
    years = _safe_input("Important years: ")
    print("")
    print("Enter additional keywords separated by commas:")
    other_keywords = _safe_input("> ")

    # Aggregate fields
    words_list = []
    
    orgs = [company, org, school, college]
    locs = [city, country, location, ssid]
    interests = [sports, teams, games, movies, shows, music, hobbies]
    techs = [tech, lang]
    projs = [projects, brands, products]
    yrs = [dates, years]
    
    custom_words = [w.strip() for w in other_keywords.split(",") if w.strip()]
    
    for category in [orgs, locs, interests, techs, projs, yrs]:
        for item in category:
            if item:
                words_list.extend([w.strip() for w in item.split(",") if w.strip()])
    
    words_list.extend(custom_words)
    
    names_count = sum(1 for x in [first_name, last_name, nickname, username, partner_name, partner_nickname, child_name, pet_name] if x)
    orgs_count = sum(1 for x in orgs if x)
    locs_count = sum(1 for x in locs if x)
    ints_count = sum(1 for x in interests if x)
    techs_count = sum(1 for x in techs if x)
    projs_count = sum(1 for x in projs if x)
    yrs_count = sum(1 for x in yrs if x)
    custom_count = len(custom_words)

    print("\\nPROFILE SUMMARY")
    print("===============")
    print(f"Names:          {names_count}")
    print(f"Organizations:  {orgs_count}")
    print(f"Locations:      {locs_count}")
    print(f"Interests:      {ints_count}")
    print(f"Technologies:   {techs_count}")
    print(f"Projects:       {projs_count}")
    print(f"Years:          {yrs_count}")
    print(f"Custom words:   {custom_count}")
    print("")
    
    if not _ask_yes_no("Continue?", default=True):
        return run_profile_wizard(show_banner=False)

    return Profile(
        name=first_name.lower(),
        surname=last_name.lower(),
        nick=nickname.lower(),
        wife=partner_name.lower(),
        wifen=partner_nickname.lower(),
        kid=child_name.lower(),
        pet=pet_name.lower(),
        company=company.lower(),
        words=words_list,
        spechars1=True,
        randnum=True,
        leetmode=True,
    )
\"\"\"

HASHFORGE_PY = \"\"\"#!/usr/bin/env python3
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

def print_banner() -> None:
    banner = r\"\"\"
╔══════════════════════════════════════╗
║             HASHFORGE                ║
║ Profile-Driven Wordlist Generator    ║
╚══════════════════════════════════════╝\"\"\"
    print(banner)


def interactive_main():
    print_banner()
    print("\\n[1] Build profile\\n[2] Load profile\\n[3] Exit\\n")
    try:
        choice = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)
        
    profile_obj = None
    if choice == "1":
        profile_obj = run_profile_wizard()
    elif choice == "2":
        path = input("Enter profile JSON path: ").strip()
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                profile_obj = Profile.from_dict(json.load(f))
        else:
            print("File not found.")
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
\"\"\"

with open("hashforge/profile/wizard.py", "w", encoding="utf-8") as f:
    f.write(WIZARD_PY)

with open("hashforge.py", "w", encoding="utf-8") as f:
    f.write(HASHFORGE_PY)

print("Updated wizard and hashforge.py")
