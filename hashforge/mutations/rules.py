"""Hashcat rule parser and evaluation engine."""

import os
from typing import List, Optional, Tuple


def decode_pos(c: str) -> int:
    """Decode a Hashcat character index (0-9, A-Z -> 0-35)."""
    if "0" <= c <= "9":
        return ord(c) - ord("0")
    elif "A" <= c <= "Z":
        return ord(c) - ord("A") + 10
    elif "a" <= c <= "z":
        return ord(c) - ord("a") + 10
    return 0


ONE_CHAR_OPS = set(":lucCtrdf{}[]qkK")
TWO_CHAR_OPS = set("$^pTD'@zZ+-.,<>_!/()")
THREE_CHAR_OPS = set("siox=*")


def tokenize_rule_line(line: str) -> List[str]:
    """Tokenize a rule line into distinct Hashcat operations."""
    line = line.strip()
    if not line or line.startswith("#"):
        return []

    tokens: List[str] = []
    i = 0
    while i < len(line):
        if line[i].isspace():
            i += 1
            continue

        c = line[i]
        if c in ONE_CHAR_OPS:
            tokens.append(c)
            i += 1
        elif c in TWO_CHAR_OPS:
            if i + 1 < len(line):
                tokens.append(line[i : i + 2])
                i += 2
            else:
                tokens.append(line[i:])
                i += 1
        elif c in THREE_CHAR_OPS:
            if i + 2 < len(line):
                tokens.append(line[i : i + 3])
                i += 3
            elif i + 1 < len(line):
                tokens.append(line[i : i + 2])
                i += 2
            else:
                tokens.append(c)
                i += 1
        else:
            # Fallback for unrecognized/extended tokens
            tokens.append(c)
            i += 1

    return tokens


def apply_op(op: str, s: str) -> Optional[str]:
    """Apply a single Hashcat operation to a string. Returns None if filtered out."""
    if not op:
        return s

    cmd = op[0]

    # --- 1-character operations ---
    if cmd == ":":
        return s
    elif cmd == "l":
        return s.lower()
    elif cmd == "u":
        return s.upper()
    elif cmd == "c":
        return s.capitalize()
    elif cmd == "C":
        return s[:1].lower() + s[1:].upper() if s else s
    elif cmd == "t":
        return s.swapcase()
    elif cmd == "r":
        return s[::-1]
    elif cmd == "d":
        return s + s
    elif cmd == "f":
        return s + s[::-1]
    elif cmd == "{":
        return s[1:] + s[:1] if s else s
    elif cmd == "}":
        return s[-1:] + s[:-1] if s else s
    elif cmd == "[":
        return s[1:] if s else s
    elif cmd == "]":
        return s[:-1] if s else s
    elif cmd == "q":
        return "".join(ch * 2 for ch in s)
    elif cmd == "k":
        return (s[1] + s[0] + s[2:]) if len(s) >= 2 else s
    elif cmd == "K":
        return (s[:-2] + s[-1] + s[-2]) if len(s) >= 2 else s

    # --- 2-character operations ---
    if len(op) >= 2:
        param = op[1]
        if cmd == "$":
            return s + param
        elif cmd == "^":
            return param + s
        elif cmd == "p":
            cnt = decode_pos(param)
            return s * (cnt + 1)
        elif cmd == "T":
            pos = decode_pos(param)
            if 0 <= pos < len(s):
                ch = s[pos]
                new_ch = ch.lower() if ch.isupper() else ch.upper()
                return s[:pos] + new_ch + s[pos + 1 :]
            return s
        elif cmd == "D":
            pos = decode_pos(param)
            if 0 <= pos < len(s):
                return s[:pos] + s[pos + 1 :]
            return s
        elif cmd == "'":
            pos = decode_pos(param)
            return s[:pos]
        elif cmd == "@":
            return s.replace(param, "")
        elif cmd == "z":
            cnt = decode_pos(param)
            return (s[:1] * cnt) + s if s else s
        elif cmd == "Z":
            cnt = decode_pos(param)
            return s + (s[-1:] * cnt) if s else s
        elif cmd == "+":
            pos = decode_pos(param)
            if 0 <= pos < len(s):
                return s[:pos] + chr((ord(s[pos]) + 1) % 256) + s[pos + 1 :]
            return s
        elif cmd == "-":
            pos = decode_pos(param)
            if 0 <= pos < len(s):
                return s[:pos] + chr((ord(s[pos]) - 1) % 256) + s[pos + 1 :]
            return s
        elif cmd == ".":
            pos = decode_pos(param)
            if 0 <= pos < len(s) - 1:
                return s[: pos + 1] + s[pos] + s[pos + 2 :]
            return s
        elif cmd == ",":
            pos = decode_pos(param)
            if 0 <= pos < len(s) - 1:
                return s[:pos] + s[pos + 1] + s[pos + 1 :]
            return s

        # Filter rules (return None if rejected)
        elif cmd == "<":
            limit = decode_pos(param)
            return s if len(s) <= limit else None
        elif cmd == ">":
            limit = decode_pos(param)
            return s if len(s) >= limit else None
        elif cmd == "_":
            target_len = decode_pos(param)
            return s if len(s) == target_len else None
        elif cmd == "!":
            return s if param not in s else None
        elif cmd == "/":
            return s if param in s else None
        elif cmd == "(":
            return s if (s and s[0] == param) else None
        elif cmd == ")":
            return s if (s and s[-1] == param) else None

    # --- 3-character operations ---
    if len(op) >= 3:
        p1, p2 = op[1], op[2]
        if cmd == "s":
            return s.replace(p1, p2)
        elif cmd == "i":
            pos = decode_pos(p1)
            if pos <= len(s):
                return s[:pos] + p2 + s[pos:]
            return s + p2
        elif cmd == "o":
            pos = decode_pos(p1)
            if pos < len(s):
                return s[:pos] + p2 + s[pos + 1 :]
            return s + p2
        elif cmd == "*":
            pos1, pos2 = decode_pos(p1), decode_pos(p2)
            if 0 <= pos1 < len(s) and 0 <= pos2 < len(s) and pos1 != pos2:
                chars = list(s)
                chars[pos1], chars[pos2] = chars[pos2], chars[pos1]
                return "".join(chars)
            return s
        elif cmd == "x":
            pos, length = decode_pos(p1), decode_pos(p2)
            return s[pos : pos + length]
        elif cmd == "=":
            pos = decode_pos(p1)
            return s if (0 <= pos < len(s) and s[pos] == p2) else None

    # Default pass-through if unrecognized
    return s


class HashcatRule:
    """Represents a compiled line of Hashcat rule operations."""

    def __init__(self, raw: str, operations: Optional[List[str]] = None):
        self.raw = raw.strip()
        self.operations = operations if operations is not None else tokenize_rule_line(self.raw)

    def apply(self, word: str) -> Optional[str]:
        """Apply all operations sequentially. Returns None if filtered out."""
        curr = word
        for op in self.operations:
            res = apply_op(op, curr)
            if res is None:
                return None
            curr = res
        return curr

    def __repr__(self) -> str:
        return f"HashcatRule('{self.raw}')"


def load_rule_file(filepath: str) -> List[HashcatRule]:
    """Safely load and compile rules from a .rule file."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Rule file not found: {filepath}")

    rules: List[HashcatRule] = []

    # Try UTF-8 first, fallback to latin-1
    content = ""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        with open(filepath, "r", encoding="latin-1", errors="replace") as f:
            lines = f.readlines()

    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            continue
        ops = tokenize_rule_line(line_clean)
        if ops:
            rules.append(HashcatRule(line_clean, ops))

    return rules
