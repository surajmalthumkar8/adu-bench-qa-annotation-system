#!/usr/bin/env python3
"""Self-validation for the ADU-Bench QA annotation system after a fresh clone.

Run from the repo root:  python verify_setup.py

Proves the whole engineered system arrived intact and wired: all 6 mandatory
(+2 video) subagents, the humanizer skill, every binding rule, the workflows,
knowledge, templates, and the python tooling. Pure standard library, so it runs
BEFORE any `pip install`; the video-pipeline runtime deps (opencv, numpy) are
checked separately as warnings, since they are only needed to ingest recordings.

Exit code 0 = every REQUIRED check passed (system is ready). 1 = something is
missing or broken (the printed FAIL lines say exactly what).
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FAILS: list[str] = []
WARNS: list[str] = []
PASSES = 0


def req(cond: bool, msg: str) -> None:
    global PASSES
    if cond:
        PASSES += 1
    else:
        FAILS.append(msg)


def warn(cond: bool, msg: str) -> None:
    global PASSES
    if cond:
        PASSES += 1
    else:
        WARNS.append(msg)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def frontmatter(txt: str) -> str:
    # "---\n<fm>\n---\n<body>" -> <fm>
    parts = txt.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""


# ---------------------------------------------------------------- 1. subagents
AGENTS = [
    "evidence-hunter", "independent-solver", "reviewer-simulator", "humanizer",
    "final-evaluator", "lessons-scribe",           # the 6 DO_TASK-chain agents
    "doc-reconstructor", "extraction-evaluator",   # video-ingest agents
]
for a in AGENTS:
    p = ROOT / ".claude" / "agents" / f"{a}.md"
    if not p.is_file():
        req(False, f"agent file missing: .claude/agents/{a}.md")
        continue
    fm = frontmatter(read(p))
    req(re.search(rf"^name:\s*{re.escape(a)}\s*$", fm, re.M) is not None,
        f"agent {a}: frontmatter name must equal '{a}'")
    req("model: opus" in fm, f"agent {a}: must be pinned 'model: opus'")
    req(re.search(r"^description:\s*\S", fm, re.M) is not None,
        f"agent {a}: must have a description")

# ---------------------------------------------------------- 2. humanizer skill
skill = ROOT / ".claude" / "skills" / "humanizer" / "SKILL.md"
sfm = frontmatter(read(skill))
req(skill.is_file(), "humanizer skill missing: .claude/skills/humanizer/SKILL.md")
req("name: humanizer" in sfm, "humanizer skill: frontmatter name must be 'humanizer'")
req("version:" in sfm, "humanizer skill: must carry a version")
req(len(read(skill)) > 20000, "humanizer skill: SKILL.md looks truncated (<20KB)")

# humanizer AGENT must invoke the skill mandatorily
hum = read(ROOT / ".claude" / "agents" / "humanizer.md")
req("Skill" in frontmatter(hum), "humanizer agent: must list the Skill tool")
req("ALWAYS" in hum and "humanizer` skill" in hum,
    "humanizer agent: must MANDATORY-invoke the humanizer skill (ALWAYS)")
req("NOTE_STYLE_CORPUS" in hum, "humanizer agent: must use the note corpus as voice sample")
# final-evaluator must verify the skill ran
fe = read(ROOT / ".claude" / "agents" / "final-evaluator.md")
req("humanizer" in fe and "skill" in fe.lower(),
    "final-evaluator: must confirm the humanizer skill ran")

# ------------------------------------------------------------------ 3. rules
for r in ["VERDICT_RULES", "EVIDENCE_RULES", "NOTES_RULES", "PLATFORM_RULES",
          "VISUAL_VERIFICATION_RULES", "WORKFLOW_RULES"]:
    req((ROOT / "system" / "rules" / f"{r}.md").is_file(),
        f"rule missing: system/rules/{r}.md")

# WORKFLOW_RULES must list all 6 chain agents (incl. lessons-scribe)
wr = read(ROOT / "system" / "rules" / "WORKFLOW_RULES.md")
req("lessons-scribe" in wr, "WORKFLOW_RULES: lessons-scribe must be in the mandatory roster")
req(len(re.findall(r"^\s*\|\s*[1-6]\s*\|\s*`", wr, re.M)) >= 6,
    "WORKFLOW_RULES: agent table must have 6 rows")

# ------------------------------------------------------------- 4. workflows
for w in ["DO_TASK", "INGEST_VIDEO", "ATTEMPT_TASK", "REVIEW_TASK", "FIX_TASK"]:
    req((ROOT / "system" / "workflows" / f"{w}.md").is_file(),
        f"workflow missing: system/workflows/{w}.md")
do = read(ROOT / "system" / "workflows" / "DO_TASK.md")
req("lessons-scribe" in do, "DO_TASK: must include the lessons-scribe learning step")
req("VISUAL_VERIFICATION" in do or "triangulation" in do.lower(),
    "DO_TASK: must reference the visual-verification / triangulation gate")

# ------------------------------------------------------------- 5. knowledge
for k in ["GOLD_PATTERNS", "NOTE_STYLE_CORPUS", "PROJECT_MODEL", "REVIEWER_MODEL",
          "TASK_ANATOMY"]:
    req((ROOT / "system" / "knowledge" / f"{k}.md").is_file(),
        f"knowledge missing: system/knowledge/{k}.md")

# --------------------------------------------------- 6. templates / checklist
for t in ["DELIVERABLE_TEMPLATE", "SUBMISSION_TEMPLATE"]:
    req((ROOT / "system" / "templates" / f"{t}.md").is_file(),
        f"template missing: system/templates/{t}.md")
req((ROOT / "system" / "checklists" / "PRE_SUBMIT_CHECKLIST.md").is_file(),
    "checklist missing: system/checklists/PRE_SUBMIT_CHECKLIST.md")
req((ROOT / "system" / "learning" / "LESSONS.md").is_file(),
    "learning log missing: system/learning/LESSONS.md")
req((ROOT / "CLAUDE.md").is_file(), "CLAUDE.md missing at repo root")

# --------------------------------------------------- 7. python tools compile
PY = ["tools/validate_submission.py", "video_pipeline/ingest.py",
      "video_pipeline/tools/label_tabs.py", "video_pipeline/tools/validate_extraction.py",
      "verify_setup.py"]
for rel in PY:
    p = ROOT / rel
    if not p.is_file():
        req(False, f"tool missing: {rel}")
        continue
    try:
        ast.parse(read(p))
        req(True, rel)
    except SyntaxError as e:
        req(False, f"{rel} has a syntax error: {e}")

# ------------------------------------------------ 8. optional runtime deps
for mod, why in [("cv2", "opencv-python — needed to ingest recordings"),
                 ("numpy", "numpy — needed to ingest recordings")]:
    try:
        __import__(mod)
        warn(True, mod)
    except Exception:
        warn(False, f"optional dep not importable: {mod} ({why}); run "
                    f"'pip install -r video_pipeline/requirements.txt'")
# RapidOCR is optional and intentionally OFF the critical path
try:
    __import__("rapidocr_onnxruntime")
    warn(True, "rapidocr (optional)")
except Exception:
    try:
        __import__("rapidocr")
        warn(True, "rapidocr (optional)")
    except Exception:
        warn(False, "optional dep not importable: rapidocr (only used by the slow "
                    "label_tabs OCR path, which the fast workflow skips)")

# --------------------------------------------------------------- 9. report
print("ADU-Bench annotation system — setup verification\n" + "=" * 52)
print(f"PASSED : {PASSES}")
print(f"WARN   : {len(WARNS)} (optional / video-ingest only)")
print(f"FAIL   : {len(FAILS)}")
for w in WARNS:
    print(f"  [warn] {w}")
for f in FAILS:
    print(f"  [FAIL] {f}")
print("=" * 52)
if FAILS:
    print("RESULT: NOT READY — fix the FAIL lines above, then re-run.")
    sys.exit(1)
print("RESULT: ALL REQUIRED CHECKS PASS — the system is intact and wired.")
if WARNS:
    print("Note: warnings are fine for annotation work; install the video-ingest "
          "deps only when you need to process a recording.")
sys.exit(0)
