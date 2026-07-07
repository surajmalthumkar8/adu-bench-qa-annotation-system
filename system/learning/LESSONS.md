# LESSONS — the system's learning loop

Every reviewer comment, SBQ, score, or newly signed-off example must land here as a
structured entry, and (when it changes behavior) as an edit to a rule/knowledge file.
This file is append-only history; the rules files are the compiled result.

## Entry format

```
### YYYY-MM-DD · task <id> · <SBQ | score | approved-example | doc-update>
- Reviewer said (verbatim): "..."
- Root cause: <which step of ATTEMPT_TASK failed and why>
- System change: <file edited + what changed> | none (one-off, reason)
```

## Seed lessons (extracted during initial reverse-engineering, 2026-07-05)

### 2026-07-05 · gold task 10 · approved-example
- Observation: verdict Wrong purely for INCOMPLETENESS — answer "u; v; w" was true but
  didn't address the rows/columns part of the question.
- System change: completeness-vs-question rule added to VERDICT_RULES step 1 and §4.

### 2026-07-05 · gold task 14 · approved-example
- Observation: answer listed set members instead of an option letter on a lettered
  question with `set_match_casefold`; annotator judged by set semantics and it was
  signed off. The Verify field outranks the surface form of the options.
- System change: Verify-field semantics table in TASK_ANATOMY §1.

### 2026-07-05 · onboarding transcript · doc-update
- Observation: transcript overrides two written ambiguities: (1) "Notes (Optional)" is
  actually required; (2) quotes must be complete — an expert's `...`-shortened quote was
  called out as the wrong way.
- System change: NOTES_RULES §1, EVIDENCE_RULES §3.

### 2026-07-05 · doc inconsistency · doc-update
- Observation: ADU guidelines say "do not use the tab names" while in-task instructions
  say cite `[Doc1 Page 5]`. Reconciliation: DocN labels are document identifiers (also in
  PDF Reference headers); "tab names" means the evidence-panel groupings ("Doc1 P5-6 /
  Doc2 P1") which can span docs. Cite DocN + document page number.
- System change: EVIDENCE_RULES §7, PROJECT_MODEL §5.

### 2026-07-05 · compulsory chain + humanizer/evaluator agents · doc-update
- Observation: Suraj mandated (1) the workflow is compulsory — every step and every
  agent runs on every pasted task, no skipping; (2) all agents on Opus 4.8; (3) a
  dedicated humanizer agent as the FINAL content editor, grounded in how teammates
  actually write, plus a final evaluator that validates the humanization; (4) ongoing
  learning from new files he adds to Others_tasks/.
- System change: new `rules/WORKFLOW_RULES.md` (compulsory execution + fixed gate
  order); new agents `.claude/agents/humanizer.md` and `final-evaluator.md` (model:
  opus); new `knowledge/NOTE_STYLE_CORPUS.md` (all 16 gold notes verbatim + style
  fingerprint incl. human-imperfection guidance); DO_TASK rewritten as a 10-step
  mandatory chain with Step 0 learning sync; CLAUDE.md, NOTES_RULES §7,
  DELIVERABLE_TEMPLATE gate list updated.

### 2026-07-05 · system repurposing · doc-update
- Observation: primary operating mode clarified by Suraj — he pastes task content +
  screenshots; Claude performs the task and returns a paste-ready submission,
  first-time-right, strongest models everywhere (all subagents pinned `model: opus`).
- System change: new `workflows/DO_TASK.md` (primary; input-completeness gate +
  screenshot transcription protocol), new `templates/DELIVERABLE_TEMPLATE.md`,
  CLAUDE.md primary-mode section, PROJECT_MODEL §6, agent frontmatter model pins.

### 2026-07-05 · STORM validation pass · doc-update
- Observation: full replay of the 16 gold tasks against the rules found zero
  false-rejects; all 7 numeric answers recompute exactly with code; validator accepts
  all 4 real citation variants found in signed-off work. Gaps logged: only 4 Verify
  types observed; no single-doc gold example exists yet.
- System change: report at `learning/VALIDATION_STORM_2026-07-05.md`; no rule changes
  needed (validation confirmed the encoding).

### 2026-07-05 · attempter guidelines internal tension · doc-update
- Observation: workflow step 8 says "add notes only if needed" but section 06 says notes
  are NOT optional. Repetition + emphasis (and the transcript) settle it: always fill notes.
- System change: NOTES_RULES §1.

### 2026-07-05 · task1 qa_016 (7ab7af2f) · first-real-run (outcome pending review)
- Task: [consistency] cross-doc, Format Int, Verify numeric_tolerance. AI answer 3.
  Full compulsory chain ran (all 5 agents via general-purpose+opus fallback, since the
  custom agent types were created mid-session). Independent solve = 3; verdict Correct;
  validator CLEAN ×2, reviewer-simulator APPROVE, humanizer no-change, final-evaluator
  SHIP + HUMANIZATION PASS. Delivered; NOT yet reviewer-scored.
- Lesson 1 (firewall leak): the needed Doc1 p34 page only appeared in captures that also
  showed the AI answer "3". Excluding those from the solver would have hidden the
  evidence; transcribing the p34 paragraph verbatim into the solver prompt preserved both
  the firewall and the evidence. Now a standing protocol.
- Lesson 2 (out-of-context number): Doc2's printed trans.deg values 4/6/≤2 describe the
  invariant subfield L, not the function field F the question asks about. The answer 3
  comes from the shared n=3 setting via Doc1's dim=trdeg(F/k) definition. Grabbing the
  nearest printed integer would have been wrong.
- System change: DO_TASK Step 4 "screenshot firewall-leak protocol"; GOLD_PATTERNS §4
  "out-of-context number trap". If reviewer feedback arrives on task1, append it here +
  edit the owning rule before the next task (WORKFLOW_RULES rule 8).

## 2026-07-06 — System hardening (Suraj directive: no wrong answers, stronger looking, a learning agent)

- What happened: after task6 shipped, Suraj asked to (a) cut extraction time/tokens so each
  task can run in its own low-cost session, and (b) harden DO_TASK — strong rules, a strong
  way of looking at every image/document, cross-check + validate + evaluate, a learning
  agent, and zero wrong answers.
- Extraction side (details in video_pipeline/learning/LESSONS.md same date): kept the safe
  Pass-1 stride win (22s); an aggressive displacement-tiling token-cut was TRIED, VALIDATED,
  and REVERTED because it silently dropped two decisive date lines from the tiles — the
  validate-before-ship discipline caught it. Tile-count reduction deferred behind a
  regression harness.
- DO_TASK side — changes made this session (all applied, not proposed):
  1. **Learning is now an AGENT, not a manual step.** New `.claude/agents/lessons-scribe.md`
     (model: opus, Read/Grep/Glob/Edit/Write). It runs LAST every task (DO_TASK step 11 /
     INGEST_VIDEO step 8): writes the LESSONS entry AND applies the owning rule/knowledge edit
     in the same session — clean runs get a short "what kept it clean" entry, caught defects
     get a root-cause + structural guard, recurring defects get escalated to a stronger guard.
     Wired into DO_TASK.md, WORKFLOW_RULES.md (roster now 6 agents; rule 8 rewritten),
     INGEST_VIDEO.md step 8, CLAUDE.md.
  2. **"Looking hard" is now a binding gate.** New `system/rules/VISUAL_VERIFICATION_RULES.md`:
     every decisive value is read off the image/PDF pixels char-by-char (Markdown is only an
     index), confusable glyphs (3↔8, 1↔7, 5↔6, 0↔O, en-dash↔hyphen) explicitly resolved,
     each value carries a `src` frame, and TWO independent reads must agree
     (evidence-hunter + independent-solver, or two frames) — a disagreement is a BLOCKING
     re-read. Added as WORKFLOW_RULES rule 10 and a DO_TASK step-5 triangulation gate.
  3. **Derived-quantity trap codified** (from task6's first Wrong verdict): a restated-operands
     answer to a range/min/max/count/grouping question is Wrong even if each operand is
     supported. Added to VERDICT_RULES §4, GOLD_PATTERNS §4, and the visual rules §3.
  4. **Agent prompts strengthened** to enforce the above: independent-solver (pixel reads +
     derived-quantity discipline + glyph confirmation), evidence-hunter (pixel `src` + clipped-
     line rule + separate-line integrity), reviewer-simulator (derived-quantity trap + visual-
     verification rejection criteria + page-outlier note check), final-evaluator (re-derive +
     pixel-anchor + derived-quantity FAIL condition).
- Token/rigor tension (acknowledged, resolved by design): adding a 6th mandatory agent and more
  checks would raise per-task tokens; the offset is the pixel-`src` + triangulation discipline —
  each decisive value is read ONCE and confirmed from two existing sources, replacing the habit of
  re-reading many overlapping tiles. Net: stronger correctness, image-reads focused on decisive
  pixels. lessons-scribe is deliberately terse (a clean run = a one-paragraph entry).
- Detection gap closed: previously "look hard" and "learn every task" lived in prose and depended
  on the orchestrator remembering. They are now an enforced gate + a mandatory agent — the two most
  common sources of a wrong verdict (mis-read pixel; un-recorded lesson that repeats) now have
  structure, not hope.
- Open/owned: (1) tile-count reduction behind a regression harness (never a scroll-distance
  stride); (2) a fast, OCR-free page-index for token-lean reading (label_tabs OCR times out — do
  NOT put it on the critical path); (3) live-time the extraction-evaluator keyframe-reuse (Stage-B
  skipped by design 4 tasks running).

## 2026-07-06 — Humanizer skill integrated as a mandatory agent step (Suraj directive)

- What happened: Suraj required the notes field to always be run through the blader
  `humanizer` skill (https://github.com/blader/humanizer) so submitted notes are concise,
  casual, plainly human — never "too smart", robotic, or AI-sounding.
- Changes made (all applied + validated):
  1. Installed the skill version-pinned in-repo: `.claude/skills/humanizer/SKILL.md`
     (blader v2.8.2, MIT, 34017 bytes, 30+ AI-tell patterns). It now shows as an invokable
     `humanizer` skill and does not depend on the ambient copy.
  2. Rewrote `.claude/agents/humanizer.md`: step 1 is now MANDATORY "run the humanizer skill
     on the note, always" (with a Read-the-SKILL.md fallback if the Skill tool can't resolve
     it inside the subagent), using `NOTE_STYLE_CORPUS.md` as the skill's voice-calibration
     sample. Added the standing "do not sound smart" prime directive (concise/casual/plain,
     flatten anything clever) and a note that our text is technical/reference — apply the
     skill's plain-voice fixes but NOT its blog-style personality/soul injection.
  3. Enforcement: `final-evaluator` now FAILs if the humanizer's report does not confirm the
     skill ran, and rejects a note that reads clever/polished ("not too smart" check).
     Made the humanizer's SKILL confirmation line a required, first return section (it was
     dropped on the first validation run — the skill DID run, but the report omitted it).
     WORKFLOW_RULES rule 5 + CLAUDE.md updated to state the skill runs every task.
- Validation (dogfooded): dispatched the humanizer agent on a deliberately over-written,
  AI-sounding draft of the task6 note (em-dashes, "It is worth noting", "underscore",
  "delineate", rule-of-three, "fundamentally incorrect"). It invoked the skill via the Skill
  tool (confirmed on follow-up), applied patterns #1/#3/#4/#7/#8/#13/#22, and returned a
  clean corpus-voice note: "The January start days are 3, 4, 3, 3 and 4, so the earliest is 3
  (2003, 2006, 2007) and the latest is 4 (2005, 2008), giving a range of 4 - 3 = 1, which is
  option D. The answer just lists all five years ... and never gives the range or picks an
  option, so it is Wrong." Every fact + the arithmetic preserved; all tells gone.
- Detection gap closed: note-voice was previously "invoke the skill IF available" (optional)
  — a note could ship AI-sounding if the skill was skipped. It is now mandatory, verified by
  the final-evaluator, and pinned in-repo so it can't silently go missing.
