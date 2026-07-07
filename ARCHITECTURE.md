# ARCHITECTURE — design decisions and rationale

## What this system is

A modular verification pipeline for ADU-Bench QA annotation, built as versioned files in
this repo: knowledge (mental models) + rules (binding, checkable) + workflows
(orchestration) + subagents (isolated reasoning roles) + a deterministic validator +
an append-only learning log. `CLAUDE.md` is the runtime entrypoint.

```
CLAUDE.md                        entrypoint & routing
system/
  knowledge/   PROJECT_MODEL · TASK_ANATOMY · REVIEWER_MODEL · GOLD_PATTERNS
  rules/       VERDICT · EVIDENCE · NOTES · PLATFORM        (binding, atomic, checkable)
  workflows/   DO_TASK (primary, paste-driven) · ATTEMPT_TASK · REVIEW_TASK · FIX_TASK
  templates/   SUBMISSION_TEMPLATE · DELIVERABLE_TEMPLATE
  checklists/  PRE_SUBMIT_CHECKLIST
  learning/    LESSONS.md                                   (append-only feedback→rule loop)
.claude/agents/  evidence-hunter · independent-solver · reviewer-simulator
tools/           validate_submission.py                     (deterministic format/consistency gate)
```

## Key design decisions (and why they differ from the initial sketch)

### 1. Three subagents, not eighteen

The suggested agent list (Temporal Reasoner, Comparison Specialist, Aggregation
Specialist, Publication Metadata Specialist, ...) contains roles that differ only in
*strategy*, not in *capability or context needs*. Implementing each as a separate agent
multiplies prompts to maintain, adds handoff loss, and buys nothing: a "Temporal
Reasoner" is the independent-solver with a two-line strategy note.

So task-type expertise is **data, not agents**: the taxonomy table in
`TASK_ANATOMY.md §2` + the routing table in `ATTEMPT_TASK.md` select a strategy the
solver applies. Adding a new task type = one table row, not a new agent.

The three agents that survive are the ones where *isolation itself* is the feature:
- **independent-solver** — must not see the AI answer (anti-anchoring firewall; you
  cannot un-see an answer inside a single context).
- **evidence-hunter** — parallelizable per document, keeps bulk page content out of the
  orchestrator's context.
- **reviewer-simulator** — adversarial stance works better in a fresh context that
  hasn't invested in the draft (no self-leniency).

Planner / Task Classifier / Workflow Manager / Validator-as-agent collapsed into the
orchestrating workflow: classification is a 30-second inline step, and a "Workflow
Manager agent" is just the workflow file executed by the main loop.

### 2. Deterministic checks are code, not model judgment

Citation format, quotes↔pages consistency, empty fields, truncation markers, AI-tell
phrases: regex-checkable, so they are checked by `tools/validate_submission.py`
(tested against gold example 5 = CLEAN; corrupted variants = REJECT). LLM attention is
reserved for what actually needs judgment. Same principle in reverse: all arithmetic in
solving/review is python, never mental math — `numeric_tolerance` tasks are won or lost
on recomputation.

### 3. Rules and knowledge are separated

`rules/` = short, binding, atomic (diffable when a reviewer correction changes policy).
`knowledge/` = explanatory mental models. Workflows reference both. This keeps the
learning loop surgical: an SBQ usually edits one rule line, not a monolithic prompt.

### 4. The reviewer is the spec

The only real acceptance test is the reviewer's 5-minute script, so it is encoded twice:
as a mental model (`REVIEWER_MODEL.md`) and as an executable adversarial gate
(reviewer-simulator + validator). Every submission must fail-to-be-rejected before it
ships. Verifiability-in-5-minutes is treated as a hard output requirement, not a nicety.

### 5. Anti-anchoring as pipeline topology

Verification tasks fail most often by anchoring on the plausible-sounding AI answer
(mistake #1 in both guideline docs). The fix is structural, not exhortative: the solve
happens in an agent that never receives the AI answer, and adjudication compares two
independently-derived answers under the Verify-field semantics.

## Continuous improvement loop

1. Reviewer feedback / SBQ / score arrives → `FIX_TASK` step 6 forces a LESSONS.md entry
   with root cause + the rule file edited.
2. New signed-off examples land in `Others_tasks/` → distill deltas into
   `GOLD_PATTERNS.md` (patterns, not memorized examples).
3. Doc contradictions → reconcile, record in LESSONS.md "doc-update" entries, and encode
   the resolution in rules (five seed reconciliations already logged).
4. Repeated manual reasoning → promote to a rule row, template, or validator check.
   (E.g., if a new Verify type appears, it gets a TASK_ANATOMY row + a VERDICT_RULES line.)

### 6. Paste-driven primary mode (added after STORM validation, 2026-07-05)

The production entry point is Suraj pasting task content + screenshots; Claude performs
the task and returns a paste-ready deliverable. Two additions this forced:
an **input-completeness gate** (never verdict "unsupported" on partial pasted evidence —
ask for the exact missing tabs) and a **screenshot transcription protocol** (decisive
values read character-by-character; unreadable ⇒ request a closer crop, never infer).
Model policy: main loop on the strongest available model; every subagent pinned
`model: opus`. See `workflows/DO_TASK.md` and `learning/VALIDATION_STORM_2026-07-05.md`.

## Deliberate non-goals (for now)

- **No browser automation of Henna/Feather.** Platform actions (claiming, Attempt URL,
  submit mirroring) carry pay/standing risk and are cheap to do by hand; automation there
  is all downside until volume justifies it.
- **No per-task memory database.** The repo IS the memory; tasks are stateless given the
  rules. Revisit if cross-task consistency requirements emerge.
- **No score-tracking dashboard yet.** Add once real score/feedback data accumulates in
  LESSONS.md (the entry format already captures what a dashboard would need).
