# ADU-Bench QA Annotation System

This repository is a production annotation system for the **ADU-Bench QA Verification**
project: verifying AI-generated answers against document evidence, on the Henna + Feather
platforms. Source-of-truth guidelines live in the repo root and `onboarding/`; the
engineered system lives in `system/`. Gold-standard signed-off examples: `Others_tasks/`.

## PRIMARY OPERATING MODE — Claude does the task

Suraj pastes task content (text + screenshots) into chat. **Claude performs the task**
and returns a paste-ready submission: the verdict to select, evidence quotes, pages
used, and the note — formatted per `system/templates/DELIVERABLE_TEMPLATE.md`.

- Any pasted task ⇒ immediately run `system/workflows/DO_TASK.md`. No preamble.
- **The workflow is COMPULSORY** (`system/rules/WORKFLOW_RULES.md`): every step, every
  task, and ALL FIVE agents dispatched every time — evidence-hunter →
  independent-solver → reviewer-simulator → humanizer → final-evaluator. No skipping,
  no inlining, no matter how simple the task looks.
- **First-time-right is the contract.** Gate chain before delivering: validator CLEAN →
  reviewer-simulator APPROVE → humanizer applied → validator CLEAN again →
  final-evaluator SHIP (incl. humanization PASS). A miss must never repeat (LESSONS loop).
- If the pasted evidence is incomplete, ask for the exact missing tabs/screenshots
  BEFORE verdicting — never judge "unsupported" on partial evidence.
- Models: main loop on the strongest available model; ALL subagents pinned
  `model: opus` (= Opus 4.8) in `.claude/agents/*`. Never downgrade any agent.
- The **humanizer is the final content editor**: the note must blend into
  `system/knowledge/NOTE_STYLE_CORPUS.md` (real teammates' notes, verbatim). The humanizer
  agent ALWAYS runs the `humanizer` skill (`.claude/skills/humanizer/`, blader v2.8.2) on
  the note — mandatory — so notes are concise, casual, plain, and never AI-sounding, robotic,
  or "too smart". The final-evaluator validates the skill ran and the voice holds.
- **Continuous learning**: at the first task of each session, check `Others_tasks/` for
  new signed-off examples and distill them into NOTE_STYLE_CORPUS + GOLD_PATTERNS
  before working (Suraj adds new ones over time).
- Platform clicks (claim, Attempt URL, Feather submit) are Suraj's side; mention them
  only when relevant.

## Prime directives

1. **Evidence only.** Never outside knowledge. Cannot verify ⇒ Wrong.
2. **Independent solve before looking at the AI answer** (anti-anchoring). Numeric work
   is done with code, never mental math.
3. **Verbatim quotes, minimal pages, note always filled** — engineered to survive the
   reviewer's 5-minute checklist.
4. Correctness over speed. Use the task's time allocation.

## How to work a task

| I need to... | Follow |
|---|---|
| **Do a task Suraj pasted (default)** | `system/workflows/DO_TASK.md` |
| **Ingest a screen recording of a task (`ingest Own_tasks/taskN`)** | `system/workflows/INGEST_VIDEO.md` — compulsory QA gates (validator + extraction-evaluator vs the base video) before DO_TASK; rules in `video_pipeline/rules/EXTRACTION_QA_RULES.md` |
| Attempt a task with direct platform access | `system/workflows/ATTEMPT_TASK.md` |
| Review a submission | `system/workflows/REVIEW_TASK.md` |
| Fix a send-back (Needs work / SBQ) | `system/workflows/FIX_TASK.md` |

Supporting material:
- Decision rules: `system/rules/` (VERDICT, EVIDENCE, NOTES, PLATFORM, VISUAL_VERIFICATION — binding)
- Mental models: `system/knowledge/` (PROJECT_MODEL, TASK_ANATOMY, REVIEWER_MODEL, GOLD_PATTERNS)
- Output shape: `system/templates/SUBMISSION_TEMPLATE.md`
- Final gate: `system/checklists/PRE_SUBMIT_CHECKLIST.md`
- Mechanical validation: `python tools/validate_submission.py <submission.md>` (must be CLEAN)

Subagents (in `.claude/agents/`, all `model: opus`, ALL mandatory per task):
`evidence-hunter` (parallel evidence sweep) · `independent-solver` (never show it the
AI answer) · `reviewer-simulator` (adversarial correctness gate) · `humanizer`
(note voice — final content editor) · `final-evaluator` (last gate: coherence +
humanization validation; must return SHIP) · `lessons-scribe` (learning agent — writes
the LESSONS entry + applies the rule edit, every task).

## Looking hard is a gate (binding)

`system/rules/VISUAL_VERIFICATION_RULES.md` governs how to read every image/document:
every **decisive value** is read off the actual image/PDF pixels char-by-char (Markdown is
only a searchable index), confusable glyphs (3↔8, 1↔7, 5↔6, 0↔O) resolved, and confirmed
by **two independent reads** (evidence-hunter + independent-solver, or two frames) before
it can carry a verdict — disagreement is a BLOCKING re-read. Derived quantities
(range/min/max/count/grouping) are re-computed with code; a **restated-operands** answer to
a derived-quantity question is Wrong (VERDICT_RULES §4, GOLD_PATTERNS "derived-quantity trap").

## Learning loop (mandatory — now an agent)

Every task ends with the `lessons-scribe` agent (DO_TASK step 11 / INGEST_VIDEO step 8): it
appends the `system/learning/LESSONS.md` entry AND applies the affected rule/knowledge edit
in the same session — clean runs included. Any reviewer feedback, SBQ, score, new guideline,
or new signed-off example still flows through it. New gold examples go to `Others_tasks/` and
get distilled into `system/knowledge/GOLD_PATTERNS.md`. If a doc contradicts the system,
reconcile and log.

## Known doc reconciliations (do not re-litigate; see LESSONS.md)

- "Notes (Optional)" is actually **required** — always fill it.
- Quotes must be **complete** — never shorten with `...`.
- Cite `[DocN Page Y]` (document page numbers), never evidence-tab labels.
- The Verify field (`casefold_exact_match` / `numeric_tolerance` / `choice_exact_match` /
  `set_match_casefold`) governs strictness and acceptable answer form.
