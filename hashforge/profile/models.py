"""Profile models for synthetic candidate profiling."""

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class Profile:
    name: str
    surname: str = ""
    nick: str = ""
    birthdate: str = ""  # DDMMYYYY
    wife: str = ""  # Partner name (HashForge legacy compatibility)
    wifen: str = ""  # Partner nick
    wifeb: str = ""  # Partner birthdate (DDMMYYYY)
    kid: str = ""  # Child name
    kidn: str = ""  # Child nick
    kidb: str = ""  # Child birthdate (DDMMYYYY)
    pet: str = ""  # Pet name
    company: str = ""  # Company name
    words: List[str] = field(default_factory=list)  # Keywords
    spechars1: bool = False  # Add special chars
    randnum: bool = False  # Add random numbers
    leetmode: bool = False  # Leet mode

    def validate(self) -> None:
        """Validate profile constraints."""
        if not self.name or not self.name.strip():
            raise ValueError("Target first name cannot be empty.")

        for label, bd in [
            ("Target birthdate", self.birthdate),
            ("Partner birthdate", self.wifeb),
            ("Child birthdate", self.kidb),
        ]:
            if bd and (len(bd) != 8 or not bd.isdigit()):
                raise ValueError(f"{label} must be exactly 8 digits (DDMMYYYY) or empty.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dict compatible with legacy HashForge format."""
        return {
            "name": self.name.strip().lower(),
            "surname": self.surname.strip().lower(),
            "nick": self.nick.strip().lower(),
            "birthdate": self.birthdate.strip(),
            "wife": self.wife.strip().lower(),
            "wifen": self.wifen.strip().lower(),
            "wifeb": self.wifeb.strip(),
            "kid": self.kid.strip().lower(),
            "kidn": self.kidn.strip().lower(),
            "kidb": self.kidb.strip(),
            "pet": self.pet.strip().lower(),
            "company": self.company.strip().lower(),
            "words": [w.strip() for w in self.words if w.strip()],
            "spechars1": "y" if self.spechars1 else "n",
            "randnum": "y" if self.randnum else "n",
            "leetmode": "y" if self.leetmode else "n",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Profile":
        """Create Profile from dict."""
        spechars1 = data.get("spechars1", False)
        if isinstance(spechars1, str):
            spechars1 = spechars1.strip().lower() == "y"

        randnum = data.get("randnum", False)
        if isinstance(randnum, str):
            randnum = randnum.strip().lower() == "y"

        leetmode = data.get("leetmode", False)
        if isinstance(leetmode, str):
            leetmode = leetmode.strip().lower() == "y"

        raw_words = data.get("words", [])
        if isinstance(raw_words, str):
            words = [w.strip() for w in raw_words.split(",") if w.strip()]
        elif isinstance(raw_words, list):
            words = [str(w).strip() for w in raw_words if str(w).strip()]
        else:
            words = []

        return cls(
            name=str(data.get("name", "")).strip().lower(),
            surname=str(data.get("surname", "")).strip().lower(),
            nick=str(data.get("nick", "")).strip().lower(),
            birthdate=str(data.get("birthdate", "")).strip(),
            wife=str(data.get("wife", "")).strip().lower(),
            wifen=str(data.get("wifen", "")).strip().lower(),
            wifeb=str(data.get("wifeb", "")).strip(),
            kid=str(data.get("kid", "")).strip().lower(),
            kidn=str(data.get("kidn", "")).strip().lower(),
            kidb=str(data.get("kidb", "")).strip(),
            pet=str(data.get("pet", "")).strip().lower(),
            company=str(data.get("company", "")).strip().lower(),
            words=words,
            spechars1=bool(spechars1),
            randnum=bool(randnum),
            leetmode=bool(leetmode),
        )
