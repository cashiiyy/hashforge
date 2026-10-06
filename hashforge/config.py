"""Configuration management for HashForge / HashForge."""

import configparser
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AppConfig:
    years: List[str] = field(default_factory=lambda: [str(y) for y in range(1990, 2026)])
    chars: List[str] = field(default_factory=lambda: ["!", "@", "#", "$", "%", "&", "*"])
    numfrom: int = 0
    numto: int = 100
    wcfrom: int = 3
    wcto: int = 32
    threshold: int = 200
    alectourl: str = "https://github.com/yangbh/Hammer/raw/b0446396e8d67a7d4e53d6666026e078262e5bab/lib/hashforge/alectodb.csv.gz"
    dicturl: str = "http://ftp.funet.fi/pub/unix/security/passwd/crack/dictionaries/"
    leet: Dict[str, str] = field(default_factory=lambda: {
        "a": "4",
        "i": "1",
        "e": "3",
        "t": "7",
        "o": "0",
        "s": "5",
        "g": "9",
        "z": "2",
    })
    max_candidates: int = 500000
    default_output_file: str = os.path.join("output", "hashforge_wordlist.txt")
    rules_dir: str = "rules"

    def to_legacy_dict(self) -> dict:
        """Convert to legacy CONFIG dictionary format used by original HashForge functions."""
        return {
            "global": {
                "years": self.years,
                "chars": self.chars,
                "numfrom": self.numfrom,
                "numto": self.numto,
                "wcfrom": self.wcfrom,
                "wcto": self.wcto,
                "threshold": self.threshold,
                "alectourl": self.alectourl,
                "dicturl": self.dicturl,
            },
            "LEET": self.leet,
        }


def load_config(filename: Optional[str] = None) -> AppConfig:
    """Load configuration from hashforge.cfg or return default configuration."""
    cfg = AppConfig()

    if not filename:
        candidate = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hashforge.cfg")
        if os.path.isfile(candidate):
            filename = candidate
        elif os.path.isfile("hashforge.cfg"):
            filename = "hashforge.cfg"

    if filename and os.path.isfile(filename):
        config = configparser.ConfigParser()
        try:
            config.read(filename, encoding="utf-8")
            if config.has_section("years") and config.has_option("years", "years"):
                cfg.years = [y.strip() for y in config.get("years", "years").split(",") if y.strip()]

            if config.has_section("specialchars") and config.has_option("specialchars", "chars"):
                raw_chars = config.get("specialchars", "chars").split(",")
                cfg.chars = [c.strip().strip("'\"") for c in raw_chars if c.strip()]

            if config.has_section("nums"):
                if config.has_option("nums", "from"):
                    cfg.numfrom = config.getint("nums", "from")
                if config.has_option("nums", "to"):
                    cfg.numto = config.getint("nums", "to")
                if config.has_option("nums", "wcfrom"):
                    cfg.wcfrom = config.getint("nums", "wcfrom")
                if config.has_option("nums", "wcto"):
                    cfg.wcto = config.getint("nums", "wcto")
                if config.has_option("nums", "threshold"):
                    cfg.threshold = config.getint("nums", "threshold")

            if config.has_section("alecto") and config.has_option("alecto", "alectourl"):
                cfg.alectourl = config.get("alecto", "alectourl")

            if config.has_section("downloader") and config.has_option("downloader", "dicturl"):
                cfg.dicturl = config.get("downloader", "dicturl")

            if config.has_section("leet"):
                leet_map = {}
                for letter in config.options("leet"):
                    leet_map[letter] = config.get("leet", letter)
                cfg.leet = leet_map
        except Exception:
            pass

    return cfg
