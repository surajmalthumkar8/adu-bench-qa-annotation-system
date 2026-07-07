# WORKFLOW: ATTEMPT_TASK — master pipeline for verifying one ADU-Bench task

Input: the task content (question, AI answer, format/verify/tags, all evidence tabs,
PDF reference). Output: a submission (verdict, quotes, pages, note) that survives the
reviewer's 5-minute script.

Orchestration notes:
- Steps 2–4 can run as parallel subagents when the task is large (many evidence pages).
- The **independent solve (step 3) must complete before the AI answer is analyzed** —
  this is the anti-anchoring barrier and the single biggest quality lever.
- Deterministic work (arithmetic, format validation) uses code, not model judgment.

## Step 0 — Intake & classification (inline, fast)

- Extract: question text, AI answer, Format, Verify, Tags, cross-doc flag, evidence tabs
  list, per-doc page inventory.
- Classify task type from Tags + question shape → pick the strategy from
  `knowledge/TASK_ANATOMY.md §2`.
- Parse the question into an **atomic requirements checklist** (entities, operations,
  exclusion clauses, exactness demands, expected answer form). Write it down; every
  requirement must later be marked satisfied/violated with evidence.

## Step 1 — Evidence inventory

Read EVERY evidence tab (not just the promising ones) and build a map:
`DocN → pages present → what's on each page (one line)`. Flag pages with tables/figures/
formulas/broken markdown → these need the PDF Reference tab.
Rationale: "not on the first page" is a listed common mistake, and Wrong-for-unsupported
verdicts are only legal after a full sweep.

## Step 2 — Evidence hunt (subagent: evidence-hunter, parallelizable per doc)

For each atomic requirement, locate candidate evidence and return verbatim quote
candidates with `DocN`/page anchors. Cross-doc: expect operands in different docs.

## Step 3 — Independent solve (subagent: independent-solver — MUST NOT see the AI answer)

Give the solver the question + evidence only. It produces its own answer with quotes and,
for numeric tasks, the full computation. Arithmetic is done with code (python), not
mental math: date spans (inclusive!), sums, means, differences, set operations.

## Step 4 — Verdict adjudication (inline)

Compare independent answer vs AI answer under the Verify-field semantics
(`rules/VERDICT_RULES.md`):
- Match ⇒ Correct. Quote the confirming evidence (every operand).
- Mismatch ⇒ re-read the decisive evidence once (was OUR reading wrong?), then Wrong.
  Quote the contradicting evidence.
- AI answer true-but-incomplete vs the question's requirements ⇒ Wrong (completeness rule).
- Evidence silent after full sweep ⇒ Wrong ("cannot verify ⇒ Wrong").
Apply special cases: MC option-only, not-answerable, exact-text, PDF-is-truth.

## Step 5 — Draft the submission

Use `templates/SUBMISSION_TEMPLATE.md`:
- Quotes: minimal decisive set, canonical format, verbatim, complete sentences.
- Pages: exactly the pages in the quotes, formatted per EVIDENCE_RULES.
- Note: reasoning bridge per NOTES_RULES (all arithmetic here).

## Step 6 — Deterministic validation (code)

Run `tools/validate_submission.py` on the draft. Fix every finding. Checks: citation
format, quotes↔pages consistency, non-empty note, no explanation-language in quotes,
no `...` truncation, verdict present.

## Step 7 — Reviewer simulation (subagent: reviewer-simulator)

Adversarial pass using `knowledge/REVIEWER_MODEL.md`: the simulator tries to REJECT the
submission via the reviewer's checklist and the 8 primed mistakes. Any CONFIRMED finding
⇒ loop back to the failing step (evidence → step 2, verdict → step 4, format → step 5).
Rework until the simulator approves. Two consecutive clean passes are not required —
one clean pass with zero findings is the bar.

## Step 8 — Humanize the note

Apply the humanizer skill (or its principles) to the Notes text ONLY: remove AI-tells,
keep 1–4 specific sentences, keep inline doc/page references. Never "humanize" the
quotes — they must stay verbatim.

## Step 9 — Final QA + platform steps

- Walk `checklists/PRE_SUBMIT_CHECKLIST.md` top to bottom.
- Confirm platform mirror plan (Feather Mark as complete + Henna Submit, Attempt URL
  already pasted) per `rules/PLATFORM_RULES.md`.
- Submit only when every checklist item is green.

## Routing table (which steps get subagents)

| Condition | Adaptation |
|---|---|
| Simple lookup (1 doc, 1 fact) | Steps 2–3 inline, no subagents; still independent-solve before reading AI answer |
| Numeric (comparison/aggregation/counterfactual/temporal) | Step 3 MUST use code for arithmetic |
| Coverage/absence | Step 2 must enumerate the FULL relevant list(s) |
| Reference-chain | Step 2 walks hops sequentially; one quote per hop |
| Table/figure/formula involved | Step 1 flags; steps 2–3 consult PDF Reference; note mentions it |
| Multi-doc ≥3 or >15 evidence pages | Parallel evidence-hunter per doc |
