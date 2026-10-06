"""Interactive terminal profile wizard for HashForge."""

import sys
from typing import Optional
from .models import Profile


def _safe_input(prompt: str, default: str = "") -> str:
    """Read input safely, returning default on EOF or keyboard interrupt."""
    try:
        val = input(prompt)
        return val.strip()
    except (EOFError, KeyboardInterrupt):
        return default


def _ask_yes_no(prompt: str, default: bool = False) -> bool:
    """Prompt for a yes/no question with default."""
    default_str = "Y/n" if default else "y/N"
    full_prompt = f"{prompt} [{default_str}]: "
    ans = _safe_input(full_prompt).lower()
    if not ans:
        return default
    return ans in ("y", "yes", "1", "true")


def _ask_date(prompt: str) -> str:
    """Prompt for an 8-digit date (DDMMYYYY) or empty."""
    while True:
        val = _safe_input(f"{prompt} (DDMMYYYY): ")
        if not val:
            return ""
        if len(val) == 8 and val.isdigit():
            return val
        print("[-] Invalid format. Please enter exactly 8 digits (DDMMYYYY) or leave blank.")


def run_profile_wizard(show_banner: bool = True) -> Profile:
    """Interactive terminal wizard to collect synthetic profile information."""
    if show_banner:
        print("\n" + "=" * 70)
        print("  HashForge - Synthetic Candidate Profile Wizard")
        print("=" * 70)
        print("[+] Defensive Security Laboratory Profile Generator")
        print("[+] Insert synthetic target information to generate a candidate dataset.")
        print("[+] Press ENTER to skip any optional fields.\n")

    # Name is mandatory
    name = ""
    while not name:
        name = _safe_input("> First Name: ").strip()
        if not name:
            print("[-] First name is required. Please enter a synthetic profile name.")

    surname = _safe_input("> Surname: ").strip()
    nick = _safe_input("> Nickname: ").strip()
    birthdate = _ask_date("> Birthdate")

    print("")
    wife = _safe_input("> Partner's name: ").strip()
    wifen = _safe_input("> Partner's nickname: ").strip()
    wifeb = _ask_date("> Partner's birthdate") if wife else ""

    print("")
    kid = _safe_input("> Child's name: ").strip()
    kidn = _safe_input("> Child's nickname: ").strip()
    kidb = _ask_date("> Child's birthdate") if kid else ""

    print("")
    pet = _safe_input("> Pet's name: ").strip()
    company = _safe_input("> Company name: ").strip()

    print("")
    words_list = []
    if _ask_yes_no("> Do you want to add some key words about the target?"):
        raw_words = _safe_input("> Please enter words, separated by comma: ")
        if raw_words:
            # clean and remove spaces
            words_list = [w.strip() for w in raw_words.split(",") if w.strip()]

    spechars1 = _ask_yes_no("> Do you want to add special chars at the end of words?")
    randnum = _ask_yes_no("> Do you want to add some random numbers at the end of words?")
    leetmode = _ask_yes_no("> Leet mode? (i.e. leet = 1337)")

    profile = Profile(
        name=name.lower(),
        surname=surname.lower(),
        nick=nick.lower(),
        birthdate=birthdate,
        wife=wife.lower(),
        wifen=wifen.lower(),
        wifeb=wifeb,
        kid=kid.lower(),
        kidn=kidn.lower(),
        kidb=kidb,
        pet=pet.lower(),
        company=company.lower(),
        words=words_list,
        spechars1=spechars1,
        randnum=randnum,
        leetmode=leetmode,
    )

    return profile
