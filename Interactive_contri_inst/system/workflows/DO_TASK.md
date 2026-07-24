# WORKFLOW: DO_TASK — SxS Interactive primary mode: Suraj pastes, Claude does it

Trigger: Suraj pastes SxS Interactive task content — a request to start a task, a
pair of responses (A and B), a single continued response, or "wrap it up". Claude
runs the pipeline and returns a paste-ready deliverable per
`../templates/DELIVERABLE_TEMPLATE.md`. Platform clicks (claim, select, type,
Resample ↺, submit) stay on Suraj's side.

**COMPULSORY EXECUTION** (`../rules/WORKFLOW_RULES.md`): every step, in order, every
paste. All agents dispatch per mode, all pinned `model: opus`. Nothing is skipped,
however obvious the pick or simple the turn.

## Step 0 — Learning sync (session's first task only)

Check `Interactive_contri_inst/reference_tasks/` and any new signed-off examples for
material not yet distilled into `../knowledge/HUMAN_VOICE_CORPUS.md` and
`../knowledge/GOLD_PATTERNS.md`; distill now. Read `../learning/LESSONS.md` and
`../learning/PROMPT_LOG.md`.

## Step 1 — Intake, mode detection, state load (BLOCKING)

Parse the paste. Load or create the task state
(`../templates/STATE_TEMPLATE.md`, kept at `Interactive_contri_inst/sessions/<task-id>_state.md`).

Detect mode:
- **MODE START** — new task, no responses yet ⇒ steps S1–S6.
- **MODE COMPARE** — a pair (A and B) is pasted ⇒ steps C1–C8.
- **MODE SINGLE** — one response only (platform continued without a pair) ⇒ C4–C8
  (no pick).
- **MODE END** — turn ≥3 and the conversation is complete, or Suraj says wrap up ⇒
  steps E1–E3.

Completeness gate: a response that is blank, truncated mid-sentence, or missing its
pair ⇒ STOP, ask Suraj by name for the missing piece (mention Resample ↺ if a panel
failed). Never judge a partial pair.

## MODE START — craft the opening prompt

- **S1** Rotate: pick the least-recently-used category from
  `../knowledge/PROMPT_PLAYBOOK.md` vs `../learning/PROMPT_LOG.md`; choose a fresh
  scenario and sketch the 3–5-turn arc it can sustain.
- **S2 (AGENT: sxs-turn-writer)** Dispatch with the category, scenario, persona,
  and arc sketch → returns the draft opening prompt + planned arc.
- **S3 (AGENT: sxs-humanizer)** Dispatch with the draft → corpus-voice final text
  (ALWAYS runs the `humanizer` skill).
- **S4** Write the deliverable draft + state file; run
  `python "Interactive_contri_inst/tools/validate_sxs_turn.py" <file>` → CLEAN.
- **S5 (AGENTS: sxs-reviewer-simulator → sxs-final-evaluator)** APPROVE → SHIP
  (with HUMANIZATION: PASS). Any finding ⇒ fix at owning step, re-run S4–S5.
- **S6** Deliver prompt + arc note; append PROMPT_LOG; dispatch sxs-lessons-scribe.

## MODE COMPARE — judge the pair, write the next turn

- **C1 (AGENT: sxs-response-auditor ×2 — blind, parallel, one message)** One
  auditor per response. Each prompt contains: conversation history + THAT response
  only. **Firewall: no mention of the other response, a comparison, or any
  leaning.** Each returns: claim/code verification (char-by-char on decisive
  content), constraint-adherence checklist (current + all earlier turns), flaw list
  with quotes, goal-advancement read.
- **C2 (AGENT: sxs-preference-judge)** Dispatch with history, both responses, both
  audit reports. Applies `../rules/PREFERENCE_RULES.md` (decision order + bias
  neutralizations) → returns PICK, decisive differentials with quotes, NEAR-TIE
  flag, draft one-line reason.
- **C3 — Adjudicate (inline).** Cross-check the judge's decisive facts against both
  audits and the pasted text itself. Any disagreement on a decisive fact ⇒ BLOCKING
  re-read before the pick stands. Confirm no trap fired (length/format/sycophancy/
  position — `../knowledge/GOLD_PATTERNS.md` trap list). Pick is now FROZEN.
- **C4 (AGENT: sxs-turn-writer)** Dispatch with history + the CHOSEN response only
  (never the loser, never the judge's reasoning) + state + turn number → returns
  the draft next user message anchored to something specific in the chosen response
  (`../rules/TURN_RULES.md`), or recommends END if the arc is complete and turn ≥3.
- **C5 (AGENT: sxs-humanizer)** Draft turn + draft reason → corpus voice (ALWAYS
  runs the `humanizer` skill). No content edits after this except via loop-back.
- **C6** Write deliverable draft + update state; run the validator → CLEAN.
- **C7 (AGENTS: sxs-reviewer-simulator → sxs-final-evaluator)** Reviewer runs the
  QA script from `../knowledge/REVIEWER_MODEL.md` adversarially → APPROVE with zero
  CONFIRMED findings. Final-evaluator checks end-to-end coherence (pick follows
  from the differentials; turn reacts to the chosen response; state consistent;
  HUMANIZATION: PASS) → SHIP. FAIL ⇒ loop to owning step (voice → C5; pick → C2–C3;
  turn → C4), re-run C6–C7.
- **C8** Deliver per template: PICK + reason + next message (or END call) + turn
  status + verification summary. Dispatch sxs-lessons-scribe with the full gate
  trace.

## MODE END — close the task

- **E1** Verify turn ≥3 and the last response completed the arc; if a pair is on
  screen, MODE COMPARE steps C1–C3 still run for the final pick.
- **E2** Reviewer-simulator + final-evaluator on the end decision (no goodbye turn —
  `../rules/TURN_RULES.md`).
- **E3** Deliver: final pick (if any), "send nothing further, submit", turn summary.
  sxs-lessons-scribe closes the task (LESSONS + PROMPT_LOG + state archived).

## Failure discipline

Reviewer feedback, a flag, or a rejection ⇒ `FIX_TASK.md` + LESSONS entry (root
cause, owning step, rule edit) BEFORE the next task. Every miss becomes structure;
no miss repeats.
