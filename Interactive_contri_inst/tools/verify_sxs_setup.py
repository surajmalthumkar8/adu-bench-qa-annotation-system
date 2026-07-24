#!/usr/bin/env python3
"""Post-setup check for the SxS Interactive system (run after cloning on a new machine).

Usage: python Interactive_contri_inst/tools/verify_sxs_setup.py   (from the repo root)
Prints SETUP OK (exit 0) when everything is in place; otherwise SETUP INCOMPLETE
(exit 1) with each missing/broken piece named.
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SYS = os.path.join(ROOT, "Interactive_contri_inst", "system")

SYSTEM_FILES = [
    "workflows/DO_TASK.md", "workflows/FIX_TASK.md",
    "rules/WORKFLOW_RULES.md", "rules/PREFERENCE_RULES.md",
    "rules/TURN_RULES.md", "rules/AUTHENTICITY_RULES.md",
    "knowledge/PROJECT_MODEL.md", "knowledge/HUMAN_VOICE_CORPUS.md",
    "knowledge/GOLD_PATTERNS.md", "knowledge/REVIEWER_MODEL.md",
    "knowledge/PROMPT_PLAYBOOK.md",
    "templates/SUBMISSION_TEMPLATE.md", "templates/DELIVERABLE_TEMPLATE.md",
    "templates/STATE_TEMPLATE.md",
    "checklists/PRE_SUBMIT_CHECKLIST.md",
    "learning/LESSONS.md", "learning/PROMPT_LOG.md",
    "learning/RESEARCH_BRIEF.md",
]
AGENTS = ["sxs-response-auditor", "sxs-preference-judge", "sxs-turn-writer",
          "sxs-humanizer", "sxs-reviewer-simulator", "sxs-final-evaluator",
          "sxs-lessons-scribe"]
OTHER = [
    ("Interactive_contri_inst/Interactive Contributor Instructions.md",
     "contributor instructions (source of truth)"),
    ("Interactive_contri_inst/tools/validate_sxs_turn.py", "turn validator"),
    ("CLAUDE.md", "repo CLAUDE.md with project routing"),
]

SAMPLE = """## MODE
START

## TURN
1 of 3-5

## PICK
N/A

## REASON
N/A

## NEXT MESSAGE
quick sanity check message for the validator, nothing fancy here.

## INTERNAL (not pasted)
- Decisive differentials: N/A
- Bias check: N/A
- Constraint ledger: none yet
- Turn anchor: n/a
- Arc position: t1
- Persona/PII scan: clean
- Gates: validator=pending
"""


def main():
    problems = []

    for rel in SYSTEM_FILES:
        p = os.path.join(SYS, rel)
        if not os.path.isfile(p):
            problems.append(f"missing system file: system/{rel}")
        elif os.path.getsize(p) == 0:
            problems.append(f"empty system file: system/{rel}")

    for rel, label in OTHER:
        if not os.path.isfile(os.path.join(ROOT, rel)):
            problems.append(f"missing {label}: {rel}")

    for a in AGENTS:
        p = os.path.join(ROOT, ".claude", "agents", f"{a}.md")
        if not os.path.isfile(p):
            problems.append(f"missing agent: .claude/agents/{a}.md")
            continue
        text = open(p, encoding="utf-8").read()
        if not re.search(r"^model:\s*opus\s*$", text, re.M):
            problems.append(f"agent {a} is not pinned 'model: opus'")
        if not text.lstrip().startswith("---"):
            problems.append(f"agent {a} has no frontmatter")

    ref = os.path.join(ROOT, "Interactive_contri_inst", "reference_tasks")
    n_refs = len([f for f in os.listdir(ref)] if os.path.isdir(ref) else [])
    if n_refs < 6:
        problems.append(f"reference_tasks has {n_refs} files; expected 6")

    sess = os.path.join(ROOT, "Interactive_contri_inst", "sessions")
    if not os.path.isdir(sess):
        try:
            os.makedirs(sess)
            print("note: created empty sessions/ directory")
        except OSError as e:
            problems.append(f"cannot create sessions/: {e}")

    validator = os.path.join(ROOT, "Interactive_contri_inst", "tools",
                             "validate_sxs_turn.py")
    if os.path.isfile(validator):
        fd, tmp = tempfile.mkstemp(suffix=".md")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(SAMPLE)
            r = subprocess.run([sys.executable, validator, tmp],
                               capture_output=True, text=True)
            if "CLEAN" not in r.stdout:
                problems.append("validator did not print CLEAN on the sanity "
                                f"sample (got: {r.stdout.strip()!r})")
        finally:
            os.unlink(tmp)

    hum = os.path.join(ROOT, ".claude", "skills", "humanizer", "SKILL.md")
    if not os.path.isfile(hum):
        print("WARN: blader humanizer skill not found at .claude/skills/humanizer/ "
              "- the sxs-humanizer agent falls back to its documented pattern list, "
              "but installing the skill is strongly recommended.")

    if problems:
        print("SETUP INCOMPLETE")
        for p in problems:
            print(f"FAIL: {p}")
        return 1
    print("SETUP OK - SxS Interactive system is ready. Paste a task to begin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
