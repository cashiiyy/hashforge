"""Interactive terminal profile wizard for HashForge."""

import sys
from typing import Optional
from .models import Profile

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def _safe_input(prompt: str, default: str = "") -> str:
    try:
        val = input(prompt)
        return val.strip()
    except (EOFError, KeyboardInterrupt):
        return default

def _ask_yes_no(prompt: str, default: bool = False) -> bool:
    default_str = "Y/n" if default else "y/N"
    full_prompt = f"{prompt} [{YELLOW}{default_str}{RESET}]: "
    ans = _safe_input(full_prompt).lower()
    if not ans:
        return default
    return ans in ("y", "yes", "1", "true")

def run_profile_wizard(show_banner: bool = True) -> Profile:
    print(f"\n{BOLD}{CYAN}TARGET PROFILE{RESET}")
    print(f"{CYAN}=============={RESET}\n")

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
    other_keywords = _safe_input(f"{YELLOW}>{RESET} ")

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

    print(f"\n{BOLD}{CYAN}PROFILE SUMMARY{RESET}")
    print(f"{CYAN}==============={RESET}\n")
    print(f"Names:          {YELLOW}{names_count}{RESET}")
    print(f"Organizations:  {YELLOW}{orgs_count}{RESET}")
    print(f"Locations:      {YELLOW}{locs_count}{RESET}")
    print(f"Interests:      {YELLOW}{ints_count}{RESET}")
    print(f"Technologies:   {YELLOW}{techs_count}{RESET}")
    print(f"Projects:       {YELLOW}{projs_count}{RESET}")
    print(f"Years:          {YELLOW}{yrs_count}{RESET}")
    print(f"Custom words:   {YELLOW}{custom_count}{RESET}")
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
