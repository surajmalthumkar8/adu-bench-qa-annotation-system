# WORKFLOW: DO_TASK — PRIMARY MODE: user pastes a task, Claude does it

Trigger: Suraj pastes task content (text and/or screenshots) into chat. Claude performs
the full verification and returns a ready-to-paste submission via
`templates/DELIVERABLE_TEMPLATE.md`. Platform actions (claiming, Attempt URL, Feather
buttons) stay on the human side.

**COMPULSORY EXECUTION** (`rules/WORKFLOW_RULES.md`): every step runs, in order, every
task. All six agents are dispatched every time — evidence-hunter, independent-solver,
reviewer-simulator, humanizer, final-evaluator, lessons-scribe — all pinned to Opus. No
step or agent is ever skipped, including for tasks that look trivial.

**First-time-right is the contract.** Asking one precise question beats delivering a
guess — but never ask for what was already provided.

**Look-hard is a gate, not a hope** (`rules/VISUAL_VERIFICATION_RULES.md`): every decisive
value is read off the actual image/PDF pixels char-by-char, confusable glyphs resolved,
and confirmed by TWO independent reads before it can carry a verdict. Derived quantities
are re-computed with code, never read off the AI answer.

## Step 0 — Learning sync (session's first task only)

`Glob Others_tasks/*.md`. Any file not yet distilled into
`knowledge/NOTE_STYLE_CORPUS.md` + `knowledge/GOLD_PATTERNS.md` gets distilled now:
notes appended verbatim to the corpus, new patterns/tags/verify-types into the
knowledge files, LESSONS.md entry recording the delta.

## Step 1 — Intake & input-completeness gate (BLOCKING)

Parse everything pasted: question, AI answer, Format / Verify / Tags / cross-doc flag,
evidence tabs, PDF reference images, screenshots.

Screenshot protocol:
- Transcribe decisive values (ISBNs, years, page numbers, table cells, option letters,
  names) **character by character**; cross-check against pasted text. On text↔image
  disagreement for layout-sensitive content, the PDF image wins.
- Unreadable decisive value ⇒ ask for a closer screenshot of that region. Never infer.

Completeness check — the paste must contain:
- [ ] Full question and AI answer (+ Format/Verify line if shown)
- [ ] ALL evidence tabs the task lists (compare against the visible tab list)
- [ ] PDF Reference content when tables/figures/formulas/exact layout are involved

Missing pieces ⇒ **STOP and ask for them by name** ("please paste the Doc2 P4-5 tab and
the PDF Reference image for Doc2 page 5"). A Wrong-for-unsupported verdict is only
legal after a full sweep. If Suraj confirms "that's everything the task shows", proceed.

## Step 2 — Classify & decompose (inline)

Tag → strategy from `knowledge/TASK_ANATOMY.md §2`. Question → atomic requirements
checklist (entities, operations, exclusion clauses, exactness demands, answer form).

## Step 3 — Evidence sweep (AGENT: evidence-hunter — mandatory)

Dispatch `evidence-hunter` with the atomic requirements + the pasted evidence (one
agent per doc when ≥3 docs or >15 pages; otherwise one agent for all docs). It returns
verbatim quote candidates with [DocN Page Y] anchors + table/figure/broken-markdown
flags. Orchestrator keeps its own DocN → pages map to cross-check coverage.

## Step 4 — Independent solve (AGENT: independent-solver — mandatory, firewall)

Dispatch `independent-solver` with question + evidence ONLY — **never the AI answer**.
All arithmetic in python (inclusive dates = end − start + 1; sums/means/sets/gaps).
It returns its answer + confidence + quotes + step-by-step work.

**Screenshot firewall-leak protocol (learned task1):** task-panel/overview screenshots
usually show the AI answer in plain sight. Any image that reveals the answer is EXCLUDED
from the solver's inputs; transcribe the evidence those images uniquely contain (e.g. a
document page that only appears in an answer-revealing capture) into the solver prompt
VERBATIM instead. The firewall is only real if the leaking pixels never reach the solver.

## Step 5 — Adjudicate (inline)

Compare independent answer vs AI answer under the Verify-field semantics
(`rules/VERDICT_RULES.md`). Mismatch ⇒ one evidence re-read, then Wrong. Incomplete vs
question ⇒ Wrong. Apply special cases (MC option-only, not-answerable, exact-text,
PDF-is-truth, **derived-quantity: restated operands = non-answer = Wrong**).

**Triangulation gate (BLOCKING, `rules/VISUAL_VERIFICATION_RULES.md`):** cross-check the
evidence-hunter's and independent-solver's reads of every decisive value. Any disagreement
⇒ re-open the pixels and resolve against the image BEFORE verdicting. No verdict rests on a
single unconfirmed read.

## Step 6 — Draft + deterministic gate

Draft per `templates/SUBMISSION_TEMPLATE.md`, write to scratchpad, run
`python tools/validate_submission.py <file>` → must print CLEAN.

## Step 7 — Adversarial gate (AGENT: reviewer-simulator — mandatory)

Dispatch `reviewer-simulator` with the full task + draft → must return APPROVE with
zero CONFIRMED findings. Any finding ⇒ fix at the owning step, re-run steps 6–7.

## Step 8 — Humanize (AGENT: humanizer — mandatory, content-final)

Dispatch `humanizer` with the draft note + verdict + reasoning facts. It rewrites the
note into the gold-corpus voice (`knowledge/NOTE_STYLE_CORPUS.md`), preserving every
fact and calculation. Quotes are never touched. Re-run the validator on the humanized
submission → CLEAN. No content edits after this step except via loop-back through it.

## Step 9 — Final evaluation (AGENT: final-evaluator — mandatory, last gate)

Dispatch `final-evaluator` with the full task + final submission. It checks end-to-end
coherence (recomputing arithmetic), rule compliance, **humanization validity against
the corpus**, and deliverable format. Must return SHIP with HUMANIZATION: PASS.
FAIL ⇒ loop to the owning step (voice issues → step 8; anything else → its step, then
8–9 again).

## Step 10 — Deliver

Respond per `templates/DELIVERABLE_TEMPLATE.md`: verdict to click, paste-ready blocks,
and the verification summary listing the gates that ran (validator CLEAN,
reviewer-simulator APPROVE, humanizer applied, final-evaluator SHIP) + what was
independently recomputed. Flag anything unusual in one line.

## Step 11 — Learn (AGENT: lessons-scribe — mandatory, last)

Dispatch `lessons-scribe` with the task id/type/tags, the final verdict + independent
answer, and the FULL gate trace (every validator/reviewer/humanizer/final-evaluator
result, each REJECT/FAIL and the fix that cleared it, any threshold that fired). It writes
the `system/learning/LESSONS.md` entry AND applies the owning rule/knowledge edit in the
same session — a clean run still gets a short entry (what kept it clean); a caught defect
gets a root-cause + structural-guard edit. A task is not done until Step 11 is written.
This institutionalises "learn from every task": the LESSONS loop is an agent, not a memory.

## Failure discipline

Reviewer feedback on delivered work ⇒ `workflows/FIX_TASK.md` + mandatory LESSONS.md
entry (root cause, owning step, rule edit) BEFORE the next task. Every miss becomes
structure; no miss repeats.
