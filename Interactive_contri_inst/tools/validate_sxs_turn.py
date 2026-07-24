#!/usr/bin/env python3
"""Mechanical validator for SxS Interactive per-paste submissions (DO_TASK S4/C6).

Usage: python validate_sxs_turn.py <submission.md>
Prints CLEAN (exit 0) when no FAIL; otherwise NOT CLEAN (exit 1) with findings.
WARN lines never block but must be consciously accepted by the orchestrator.

Section format: system/templates/SUBMISSION_TEMPLATE.md (## MODE / ## TURN /
## PICK / ## REASON / ## NEXT MESSAGE / ## INTERNAL). Rules enforced:
system/rules/AUTHENTICITY_RULES.md + TURN_RULES.md + PREFERENCE_RULES.md.

A NEXT MESSAGE whose first line is exactly "[raw-paste]" (a pasted error/snippet
prompt, task6-style) skips the voice/length/formatting checks; the orchestrator
strips that marker before delivering.
"""
import re
import sys

MODES = ["START", "COMPARE", "SINGLE", "END"]
PICKS = ["A", "B", "N/A"]

# AI-tell vocabulary banned in user-side text (AUTHENTICITY_RULES hard bans).
BANNED_VOCAB = [
    "delve", "crucial", "pivotal", "moreover", "furthermore", "additionally",
    "comprehensive", "leverage", "utilize", "robust", "nuanced", "underscore",
    "testament", "intricate", "tapestry", "vibrant", "streamline", "foster",
    "i appreciate", "certainly", "kindly",
]
# Zero instances in the human corpus — banned outright.
GRATITUDE = [r"\bthanks\b", r"\bthank you\b", r"\bthx\b", r"\bappreciate\b",
             r"\bgreat answer\b", r"\bawesome answer\b"]
# Reason field: surface-feature justifications are never acceptable.
BANNED_REASONS = ["better formatted", "more detailed", "more comprehensive",
                  "nicely formatted", "well formatted", "well structured",
                  "instruction following", "accuracy", "rubric", "criteria"]

INTERNAL_KEYS = ["Decisive differentials", "Bias check", "Constraint ledger",
                 "Turn anchor", "Persona/PII", "Gates"]

END_SENTINEL = "END - send nothing further"


def section(text, name):
    m = re.search(rf"^## {re.escape(name)}\b[^\n]*$(.*?)(?=^## |\Z)", text,
                  re.M | re.S)
    return m.group(1).strip() if m else None


def strip_comments(s):
    return re.sub(r"<!--.*?-->", "", s, flags=re.S).strip()


def check_user_text(label, body, fails, warns, max_words=80, warn_words=60):
    """Voice checks shared by NEXT MESSAGE and REASON."""
    words = len(body.split())
    if words > max_words:
        fails.append(f"{label} is {words} words; hard cap {max_words} "
                     "(corpus max is ~55)")
    elif words > warn_words:
        warns.append(f"{label} is {words} words; corpus turns are usually well "
                     f"under {warn_words}")
    if re.search(r"[—–]", body):
        fails.append(f"{label} contains an em/en dash - real user turns never do")
    if re.search(r"[“”‘’]", body):
        fails.append(f"{label} contains curly quotes - use straight quotes")
    if "…" in body:
        fails.append(f"{label} contains an ellipsis character")
    low = body.lower()
    for term in BANNED_VOCAB:
        if re.search(rf"\b{re.escape(term)}\b", low):
            fails.append(f"{label} contains AI-tell vocabulary: {term!r}")
    for pat in GRATITUDE:
        if re.search(pat, low):
            fails.append(f"{label} thanks/praises the assistant - zero instances "
                         "exist in the human corpus")
    # Markdown formatting in a user turn.
    for line in body.splitlines():
        ls = line.strip()
        if re.match(r"^([-*#]|\d+[.)])\s", ls) or "**" in ls:
            fails.append(f"{label} contains list/heading/bold formatting - user "
                         "turns are plain sentences")
            break
    if ";" in body:
        warns.append(f"{label} contains a semicolon - real users almost never "
                     "use them")
    if re.search(r"\bnot (just|only)\b.*\bbut\b", low):
        warns.append(f"{label} uses negative parallelism ('not just X but Y') - "
                     "an AI tell; rephrase")


def main(path):
    fails, warns = [], []
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"NOT CLEAN\nFAIL: cannot read {path}: {e}")
        return 1

    mode = strip_comments(section(text, "MODE") or "")
    turn = strip_comments(section(text, "TURN") or "")
    pick = strip_comments(section(text, "PICK") or "")
    reason = strip_comments(section(text, "REASON") or "")
    message = section(text, "NEXT MESSAGE")
    internal = section(text, "INTERNAL")

    # --- MODE ---
    if mode not in MODES:
        fails.append(f"MODE must be one of {MODES}; got: {mode!r}")

    # --- TURN ---
    n = None
    m = re.search(r"\b([1-9]\d*)\b", turn or "")
    if not turn or not m:
        fails.append("TURN section missing or has no turn number")
    else:
        n = int(m.group(1))
        if n > 5:
            fails.append(f"TURN {n} exceeds the 5-turn maximum")
        if mode == "END" and n < 3:
            fails.append(f"END at turn {n}: minimum is 3 user turns")
        if mode == "START" and n != 1:
            fails.append(f"MODE START must be Turn 1; got {n}")

    # --- PICK ---
    if pick not in PICKS:
        fails.append(f"PICK must be one of {PICKS}; got: {pick!r}")
    else:
        if mode == "COMPARE" and pick == "N/A":
            fails.append("MODE COMPARE requires PICK A or B")
        if mode in ("START", "SINGLE") and pick != "N/A":
            fails.append(f"MODE {mode} must have PICK N/A")

    # --- NEXT MESSAGE ---
    if not message or not message.strip():
        fails.append("NEXT MESSAGE section missing or empty")
    else:
        body = message.strip()
        if mode == "END":
            if not body.startswith("END"):
                fails.append("MODE END: NEXT MESSAGE must be the END sentinel "
                             f"({END_SENTINEL!r})")
        else:
            raw = body.splitlines()[0].strip() == "[raw-paste]"
            if raw:
                if mode != "START":
                    warns.append("[raw-paste] outside MODE START - confirm a "
                                 "mid-conversation paste is genuinely natural")
            else:
                check_user_text("NEXT MESSAGE", body, fails, warns)

    # --- REASON ---
    if mode == "COMPARE":
        if not reason:
            fails.append("REASON section missing (write one or put N/A)")
        elif reason != "N/A":
            check_user_text("REASON", reason, fails, warns,
                            max_words=40, warn_words=25)
            low = reason.lower()
            for term in BANNED_REASONS:
                if term in low:
                    fails.append(f"REASON justifies by surface features/rubric: "
                                 f"{term!r} - cite the content differential")

    # --- INTERNAL ---
    if internal is None:
        fails.append("INTERNAL section missing - gates need the verification "
                     "record")
    else:
        for key in INTERNAL_KEYS:
            if key.lower() not in internal.lower():
                warns.append(f"INTERNAL record is missing '{key}'")
        if mode == "COMPARE" and re.search(
                r"Decisive differentials:\s*(N/A|none)", internal, re.I):
            fails.append("MODE COMPARE with no decisive differentials recorded - "
                         "the pick must cite what decided it")

    for w in warns:
        print(f"WARN: {w}")
    if fails:
        print("NOT CLEAN")
        for f in fails:
            print(f"FAIL: {f}")
        return 1
    print("CLEAN")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python validate_sxs_turn.py <submission.md>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
