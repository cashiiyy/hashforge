"""Legacy HashForge compatibility module for HashForge."""

import argparse
import configparser
import csv
import gzip
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Any

__author__ = "Mebus"
__license__ = "GPL"
__version__ = "3.3.1"

CONFIG: Dict[str, Any] = {}


def read_config(filename: str) -> bool:
    """Read the given configuration file and update global variables to reflect changes (CONFIG)."""
    if not os.path.isfile(filename):
        alt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)
        if os.path.isfile(alt_path):
            filename = alt_path

    if os.path.isfile(filename):
        config = configparser.ConfigParser()
        config.read(filename, encoding="utf-8")

        CONFIG["global"] = {
            "years": config.get("years", "years").split(","),
            "chars": config.get("specialchars", "chars").split(","),
            "numfrom": config.getint("nums", "from"),
            "numto": config.getint("nums", "to"),
            "wcfrom": config.getint("nums", "wcfrom"),
            "wcto": config.getint("nums", "wcto"),
            "threshold": config.getint("nums", "threshold"),
            "alectourl": config.get("alecto", "alectourl"),
            "dicturl": config.get("downloader", "dicturl"),
        }

        leetc = {}
        letters = {"a", "i", "e", "t", "o", "s", "g", "z"}
        for letter in letters:
            leetc[letter] = config.get("leet", letter)

        CONFIG["LEET"] = leetc
        return True
    else:
        print("Configuration file " + filename + " not found!")
        sys.exit("Exiting.")
        return False


def make_leet(x: str) -> str:
    """Convert string to leet."""
    if "LEET" in CONFIG:
        for letter, leetletter in CONFIG["LEET"].items():
            x = x.replace(letter, leetletter)
    return x


def concats(seq, start, stop):
    for mystr in seq:
        for num in range(start, stop):
            yield mystr + str(num)


def komb(seq, start, special=""):
    for mystr in seq:
        for mystr1 in start:
            yield mystr + special + mystr1


def print_to_file(filename, unique_list_finished):
    unique_list_finished.sort()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(os.linesep.join(unique_list_finished))

    lines = 0
    with open(filename, "r", encoding="utf-8") as f:
        for _ in f:
            lines += 1

    try:
        print(
            "[+] Saving dictionary to \033[1;31m"
            + filename
            + "\033[1;m, counting \033[1;31m"
            + str(lines)
            + " words.\033[1;m"
        )
    except UnicodeEncodeError:
        safe_name = filename.encode("ascii", errors="replace").decode("ascii")
        print(
            "[+] Saving dictionary to \033[1;31m"
            + safe_name
            + "\033[1;m, counting \033[1;31m"
            + str(lines)
            + " words.\033[1;m"
        )
    try:
        if hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
            inspect = input("> Hyperspeed Print? (Y/n) : ").lower()
        else:
            inspect = "n"
    except (EOFError, StopIteration, KeyboardInterrupt):
        inspect = "n"

    if inspect == "y":
        try:
            with open(filename, "r+", encoding="utf-8") as wlist:
                data = wlist.readlines()
                for line in data:
                    print("\033[1;32m[" + filename + "] \033[1;33m" + line)
                    time.sleep(0.0001)
                    os.system("cls" if os.name == "nt" else "clear")
        except Exception as e:
            print("[ERROR]: " + str(e))

    try:
        print(
            "[+] Now load your pistolero with \033[1;31m"
            + filename
            + "\033[1;m and shoot! Good luck!"
        )
    except UnicodeEncodeError:
        safe_name = filename.encode("ascii", errors="replace").decode("ascii")
        print(
            "[+] Now load your pistolero with \033[1;31m"
            + safe_name
            + "\033[1;m and shoot! Good luck!"
        )


def print_cow():
    print(" ___________ ")
    print(" \033[07m  hashforge.py! \033[27m                # \033[07mC\033[27mommon")
    print("      \\                     # \033[07mU\033[27mser")
    print("       \\   \033[1;31m,__,\033[1;m             # \033[07mP\033[27masswords")
    print("        \\  \033[1;31m(\033[1;moo\033[1;31m)____\033[1;m         # \033[07mP\033[27mrofiler")
    print("           \033[1;31m(__)    )\\ \033[1;m  ")
    print("           \033[1;31m   ||--|| \033[1;m\033[05m*\033[25m\033[1;m      [ Muris Kurgas | j0rgan@remote-exploit.org ]")
    print("                            [ Mebus | https://github.com/Mebus/]\r\n")


def version():
    """Display version"""
    print("\r\n	\033[1;31m[ hashforge.py ]  " + __version__ + "\033[1;m\r\n")
    print("	* Hacked up by j0rgan - j0rgan@remote-exploit.org")
    print("	* http://www.remote-exploit.org\r\n")
    print("	Take a look ./README.md file for more info about the program\r\n")


def improve_dictionary(file_to_open):
    """Implementation of the -w option."""
    kombinacija = {}
    komb_unique = {}

    if not os.path.isfile(file_to_open):
        sys.exit("Error: file " + file_to_open + " does not exist.")

    chars = CONFIG["global"]["chars"]
    years = CONFIG["global"]["years"]
    numfrom = CONFIG["global"]["numfrom"]
    numto = CONFIG["global"]["numto"]

    with open(file_to_open, "r", encoding="utf-8", errors="replace") as fajl:
        listic = fajl.readlines()

    listica = []
    for x in listic:
        listica += x.split()

    print("\r\n      *************************************************")
    print("      *                    \033[1;31mWARNING!!!\033[1;m                 *")
    print("      *         Using large wordlists in some         *")
    print("      *       options bellow is NOT recommended!      *")
    print("      *************************************************\r\n")

    try:
        conts = input("> Do you want to concatenate all words from wordlist? Y/[N]: ").lower()
    except (EOFError, StopIteration, KeyboardInterrupt):
        conts = "n"

    if conts == "y" and len(listic) > CONFIG["global"]["threshold"]:
        print("\r\n[-] Maximum number of words for concatenation is " + str(CONFIG["global"]["threshold"]))
        print("[-] Check configuration file for increasing this number.\r\n")
        try:
            conts = input("> Do you want to concatenate all words from wordlist? Y/[N]: ").lower()
        except (EOFError, StopIteration, KeyboardInterrupt):
            conts = "n"

    cont = [""]
    if conts == "y":
        for cont1 in listica:
            for cont2 in listica:
                if listica.index(cont1) != listica.index(cont2):
                    cont.append(cont1 + cont2)

    spechars = [""]
    try:
        spechars1 = input("> Do you want to add special chars at the end of words? Y/[N]: ").lower()
    except (EOFError, StopIteration, KeyboardInterrupt):
        spechars1 = "n"

    if spechars1 == "y":
        for spec1 in chars:
            spechars.append(spec1)
            for spec2 in chars:
                spechars.append(spec1 + spec2)
                for spec3 in chars:
                    spechars.append(spec1 + spec2 + spec3)

    try:
        randnum = input("> Do you want to add some random numbers at the end of words? Y/[N]:").lower()
    except (EOFError, StopIteration, KeyboardInterrupt):
        randnum = "n"

    try:
        leetmode = input("> Leet mode? (i.e. leet = 1337) Y/[N]: ").lower()
    except (EOFError, StopIteration, KeyboardInterrupt):
        leetmode = "n"

    for i in range(6):
        kombinacija[i] = [""]

    kombinacija[0] = list(komb(listica, years))
    if conts == "y":
        kombinacija[1] = list(komb(cont, years))
    if spechars1 == "y":
        kombinacija[2] = list(komb(listica, spechars))
        if conts == "y":
            kombinacija[3] = list(komb(cont, spechars))
    if randnum == "y":
        kombinacija[4] = list(concats(listica, numfrom, numto))
        if conts == "y":
            kombinacija[5] = list(concats(cont, numfrom, numto))

    print("\r\n[+] Now making a dictionary...")
    print("[+] Sorting list and removing duplicates...")

    for i in range(6):
        komb_unique[i] = list(dict.fromkeys(kombinacija[i]).keys())

    komb_unique[6] = list(dict.fromkeys(listica).keys())
    komb_unique[7] = list(dict.fromkeys(cont).keys())

    uniqlist = []
    for i in range(8):
        uniqlist += komb_unique[i]

    unique_lista = list(dict.fromkeys(uniqlist).keys())
    unique_leet = []
    if leetmode == "y":
        for x in unique_lista:
            unique_leet.append(make_leet(x))

    unique_list = unique_lista + unique_leet
    unique_list_finished = [
        x for x in unique_list if len(x) > CONFIG["global"]["wcfrom"] and len(x) < CONFIG["global"]["wcto"]
    ]

    print_to_file(file_to_open + ".hashforge.txt", unique_list_finished)


def interactive(output_file="output/hashforge_wordlist.txt", dry_run=False, max_candidates=500000, rule_file=None):
    """Implementation of interactive terminal profile wizard with HashForge workflow.
    Primary UX:
    Profile questions
          ↓
    Base candidate generation
          ↓
    Ask whether to add transformation
          ↓
    Show available transformations
          ↓
    Select one / ENTER for none
          ↓
    Bounded transformation
          ↓
    output/hashforge_wordlist.txt
    """
    print("\r\n[+] Defensive Security Laboratory Profile Generator")
    print("[+] Insert the information about the synthetic target to make a dictionary")
    print("[+] If you don't know all the info, just hit enter when asked! ;)\r\n")

    profile = {}
    try:
        name = input("> First Name: ").lower().strip()
        while len(name) == 0:
            print("\r\n[-] You must enter a name at least!")
            name = input("> Name: ").lower().strip()
        profile["name"] = name

        profile["surname"] = input("> Surname: ").lower()
        profile["nick"] = input("> Nickname: ").lower()
        birthdate = input("> Birthdate (DDMMYYYY): ")
        while len(birthdate) != 0 and len(birthdate) != 8:
            print("\r\n[-] You must enter 8 digits for birthday!")
            birthdate = input("> Birthdate (DDMMYYYY): ")
        profile["birthdate"] = birthdate
        print("\r\n")

        profile["wife"] = input("> Partners) name: ").lower()
        profile["wifen"] = input("> Partners) nickname: ").lower()
        wifeb = input("> Partners) birthdate (DDMMYYYY): ")
        while len(wifeb) != 0 and len(wifeb) != 8:
            print("\r\n[-] You must enter 8 digits for birthday!")
            wifeb = input("> Partners birthdate (DDMMYYYY): ")
        profile["wifeb"] = wifeb
        print("\r\n")

        profile["kid"] = input("> Child's name: ").lower()
        profile["kidn"] = input("> Child's nickname: ").lower()
        kidb = input("> Child's birthdate (DDMMYYYY): ")
        while len(kidb) != 0 and len(kidb) != 8:
            print("\r\n[-] You must enter 8 digits for birthday!")
            kidb = input("> Child's birthdate (DDMMYYYY): ")
        profile["kidb"] = kidb
        print("\r\n")

        profile["pet"] = input("> Pet's name: ").lower()
        profile["company"] = input("> Company name: ").lower()
        print("\r\n")

        words1 = input("> Do you want to add some key words about the victim? Y/[N]: ").lower()
        words2 = ""
        if words1 == "y":
            words2 = input("> Please enter the words, separated by comma. [i.e. hacker,juice,black], spaces will be removed: ").replace(" ", "")
        profile["words"] = [w for w in words2.split(",") if w]

        profile["spechars1"] = input("> Do you want to add special chars at the end of words? Y/[N]: ").lower()
        profile["randnum"] = input("> Do you want to add some random numbers at the end of words? Y/[N]:").lower()
        profile["leetmode"] = input("> Leet mode? (i.e. leet = 1337) Y/[N]: ").lower()
    except (EOFError, StopIteration, KeyboardInterrupt):
        if not profile.get("name"):
            profile["name"] = "test"

    from .profile.models import Profile as HFProfile
    from .generators.combinations import generate_base_candidates
    from .hashcat.discovery import discover_rule_files, prompt_select_rule
    from .hashcat.estimator import estimate_search_space
    from .mutations.rules import load_rule_file
    from .mutations.engine import transform_candidates_stream
    from .output.writer import stream_candidates_to_file

    print("\r\n[+] Now generating base candidate dataset...")
    hf_profile = HFProfile.from_dict(profile)
    wcfrom = CONFIG.get("global", {}).get("wcfrom", 3)
    wcto = CONFIG.get("global", {}).get("wcto", 32)
    base_candidates = generate_base_candidates(
        hf_profile,
        min_len=wcfrom,
        max_len=wcto,
        max_candidates=max_candidates,
    )
    print(f"[+] Generated {len(base_candidates):,} deduplicated base candidates.")

    selected_rule_path = rule_file
    if not selected_rule_path:
        try:
            add_rule_ans = input("\n> Add a transformation profile? [y/N]: ").strip().lower()
        except (EOFError, StopIteration, KeyboardInterrupt):
            add_rule_ans = "n"

        if add_rule_ans in ("y", "yes", "1"):
            rules_found = discover_rule_files("rules")
            chosen_meta = prompt_select_rule(rules_found)
            if chosen_meta:
                selected_rule_path = chosen_meta.path

    loaded_rules = []
    rule_name = "None (Base Profile Only)"
    if selected_rule_path and os.path.isfile(selected_rule_path):
        try:
            loaded_rules = load_rule_file(selected_rule_path)
            rule_name = os.path.basename(selected_rule_path)
        except Exception:
            pass

    report = estimate_search_space(
        base_count=len(base_candidates),
        rule_count=len(loaded_rules),
        rule_name=rule_name,
        min_len=wcfrom,
        max_len=wcto,
        max_candidates=max_candidates,
    )
    print(report.summary())

    if dry_run:
        print("[*] Dry-run enabled. Skipping file generation.")
        return

    print(f"[+] Streaming resulting candidate dataset to {output_file}...")
    candidate_stream = transform_candidates_stream(
        base_candidates=base_candidates,
        rules=loaded_rules,
        min_len=wcfrom,
        max_len=wcto,
        max_candidates=max_candidates,
    )
    stats = stream_candidates_to_file(candidate_stream, output_path=output_file)
    print(
        f"[+] Saving dictionary to \033[1;31m{output_file}\033[1;m, counting \033[1;31m{stats['count']:,}\033[1;m words ({stats['size_formatted']})."
    )

    if profile.get("name"):
        legacy_file = profile["name"] + ".txt"
        if os.path.normpath(legacy_file) != os.path.normpath(output_file):
            try:
                import shutil
                shutil.copyfile(output_file, legacy_file)
            except Exception:
                pass


def generate_wordlist_from_profile(profile, output_file=None):
    """Generates a wordlist from a given profile."""
    from .profile.models import Profile as HFProfile
    from .generators.combinations import generate_base_candidates

    if not CONFIG:
        read_config("hashforge.cfg")

    hf_profile = HFProfile.from_dict(profile) if isinstance(profile, dict) else profile
    wcfrom = CONFIG.get("global", {}).get("wcfrom", 3)
    wcto = CONFIG.get("global", {}).get("wcto", 32)
    cands = generate_base_candidates(hf_profile, min_len=wcfrom, max_len=wcto)

    target_name = profile["name"] if isinstance(profile, dict) else profile.name
    dest = output_file if output_file else (target_name + ".txt")
    print_to_file(dest, cands)


def download_http(url, targetfile):
    print("[+] Downloading " + targetfile + " from " + url + " ... ")
    webFile = urllib.request.urlopen(url)
    localFile = open(targetfile, "wb")
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()


def alectodb_download():
    """Download csv from alectodb and save into local file."""
    url = CONFIG["global"]["alectourl"]
    print("\r\n[+] Checking if alectodb is not present...")
    targetfile = "alectodb.csv.gz"

    if not os.path.isfile(targetfile):
        download_http(url, targetfile)

    with gzip.open(targetfile, "rt", encoding="utf-8", errors="replace") as f:
        data = csv.reader(f)
        usernames = []
        passwords = []
        for row in data:
            if len(row) > 6:
                usernames.append(row[5])
                passwords.append(row[6])

    gus = sorted(list(set(usernames)))
    gpa = sorted(list(set(passwords)))

    print("\r\n[+] Exporting to alectodb-usernames.txt and alectodb-passwords.txt\r\n[+] Done.")
    with open("alectodb-usernames.txt", "w", encoding="utf-8") as f:
        f.write(os.linesep.join(gus))

    with open("alectodb-passwords.txt", "w", encoding="utf-8") as f:
        f.write(os.linesep.join(gpa))


def mkdir_if_not_exists(dire):
    if not os.path.isdir(dire):
        os.makedirs(dire, exist_ok=True)


def download_wordlist_http(filedown):
    """Download wordlists via HTTP repository index."""
    arguments = {
        1: ("albanian", ("albanian.gz",)),
        2: ("arabic", ("arabic.gz",)),
        3: ("armhenian", ("armhenian.gz",)),
        4: ("azerbaijani", ("azerbaijani.gz",)),
        16: ("hindi", ("hindu-names.gz",)),
        31: ("russian", ("russian.lst.gz", "russian_words.koi8.gz")),
    }
    intfiledown = int(filedown)
    if intfiledown in arguments:
        dire = os.path.join("dictionaries", arguments[intfiledown][0])
        mkdir_if_not_exists(dire)
        files_to_download = arguments[intfiledown][1]
        for fi in files_to_download:
            url = CONFIG["global"]["dicturl"] + arguments[intfiledown][0] + "/" + fi
            tgt = os.path.join(dire, fi)
            download_http(url, tgt)
        print("[+] files saved to " + dire)
    else:
        print("[-] leaving.")


def download_wordlist():
    """Implementation of -l switch."""
    print("Choose language dictionary to download:")
    print("16: hindi, 31: russian")
    try:
        filedown = input("> ")
    except (EOFError, StopIteration, KeyboardInterrupt):
        filedown = "16"
    download_wordlist_http(filedown)


def get_parser():
    """Create and return argument parser."""
    parser = argparse.ArgumentParser(
        description="Common User Passwords Profiler (HashForge Modernized Defensive Suite)"
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-i", "--interactive", action="store_true", help="Interactive questions for user password profiling (HashForge wizard)")
    group.add_argument("-w", dest="improve", metavar="FILENAME", help="Improve existing dictionary")
    group.add_argument("-l", dest="download_wordlist", action="store_true", help="Download huge wordlists from repository")
    group.add_argument("-a", dest="alecto", action="store_true", help="Parse default usernames and passwords from Alecto DB")
    group.add_argument("-v", "--version", action="store_true", help="Show version")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-r", "--rule", metavar="RULE", help="Hashcat mutation rule file (e.g. best66.rule)")
    parser.add_argument("--dry-run", action="store_true", help="Perform search-space estimation dry-run without writing output")
    parser.add_argument("-o", "--output", metavar="PATH", default="output/hashforge_wordlist.txt", help="Output file path (default: output/hashforge_wordlist.txt)")
    parser.add_argument("--max-candidates", type=int, default=500000, help="Safety limit on candidate count (default: 500,000)")
    return parser


def main():
    """Command-line interface to the hashforge / HashForge utility."""
    cfg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hashforge.cfg")
    read_config(cfg_path if os.path.isfile(cfg_path) else "hashforge.cfg")

    parser = get_parser()
    args = parser.parse_args()

    if not args.quiet:
        print_cow()

    if args.version:
        version()
    elif args.interactive:
        interactive(
            output_file=args.output,
            dry_run=args.dry_run,
            max_candidates=args.max_candidates,
            rule_file=args.rule,
        )
    elif args.download_wordlist:
        download_wordlist()
    elif args.alecto:
        alectodb_download()
    elif args.improve:
        improve_dictionary(args.improve)
    else:
        parser.print_help()
