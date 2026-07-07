# INGEST_VIDEO — screen recording → verified reconstructed evidence → DO_TASK

Trigger: Suraj says `ingest Own_tasks/taskN` (or provides a recording path).
Purpose: turn `recording.mp4` into verified reconstructed documents so DO_TASK runs
with zero manual screenshots. **The base video is the source of truth at every step.**

Binding rules: `video_pipeline/rules/EXTRACTION_QA_RULES.md` (QA gate),
`video_pipeline/ARCHITECTURE.md` §6 (reconstruction spec),
`video_pipeline/RECORDING_SOP.md` (input quality).
Constraints (binding): Claude in-session only — no external LLM APIs; no Feather/Henna
portal access; open-source CPU tools only (ffmpeg, OpenCV, RapidOCR).

## Gate chain (compulsory, in order — mirrors DO_TASK's own gate philosophy)

```
pipeline output → [Stage A: validate_extraction.py CLEAN/WARN]
               → reconstruction (doc-reconstructor)
               → [Stage A re-run: CLEAN/WARN incl. text checks]
               → [Stage B: extraction-evaluator PASS]
               → completeness gate (BLOCKING)
               → DO_TASK step 1
```

No step may be skipped, inlined, or reordered. A FAIL at any gate enters the bounded
repair loop (EXTRACTION_QA_RULES §5) — max 3 targeted iterations, monotone
improvement, keep best-ever, escalate to Suraj on exhaustion.

## Speed profile (task3 lesson — extraction is means, DO_TASK is the end)

Extraction must not eat the task's time budget (target: a few minutes, not the bulk).
The gates' *intent* is fixed — full tab coverage + decisive values verified against the
base video — but the slow *mechanisms* may be swapped for faster equivalents that give
the SAME assurance. Sanctioned fast path:

1. **Skip `label_tabs.py` OCR when the pasted task already lists the tabs.** The task
   card enumerates every evidence tab (e.g. "Doc1 P38-39, Doc2 P42-43, Doc3 P19, PDF").
   That list IS the completeness contract — you don't need ~100 s of breadcrumb OCR to
   rediscover it (and on task3 it mis-grouped anyway, folding 3 tabs into one). Instead
   read the breadcrumb of a handful of *boundary* keyframes to shard tiles per tab, and
   write the corrected `tab_groups.json` by hand. Only fall back to `label_tabs.py` when
   the tab list is unknown.
2. **Self-reconstruct short decisive tabs instead of dispatching an agent.** A tab that
   spans ≤2–3 distinct keyframes you have already read is faster to transcribe inline
   (verbatim, with `<!-- src: -->` tags) than to hand to a subagent. Reserve
   `doc-reconstructor` dispatches for long / dense tabs (≥~6 tiles). Images remain
   ground truth either way.
3. **Skip the slow A7-OCR / Stage-B re-runs when the decisive values are already
   frame-verified AND triangulated.** If you have read the decisive figures directly off
   the base keyframes and they are independently confirmed by ≥2 sources (e.g. the same
   fact transcribed by two different reconstructors, or two documents that agree), the
   silent-OCR-loss failure mode A7/Stage-B exist to catch is already ruled out. Record
   this as a deliberate, justified deviation in the run's LESSONS entry — never as a
   silent skip. Any decisive value that is single-sourced or unread still gets Stage B.

Everything else (coverage invariant, completeness gate, all 5 DO_TASK agents, the
first-time-right gate chain) stays mandatory. The fast path trims redundant *verification
of already-verified content*, not verification itself.

## Steps

- **Step 0 — Preconditions + learning sync.** Check `video_pipeline/learning/LESSONS.md`
  for entries newer than the last run and apply any changed thresholds/rules. Confirm
  `ingest/manifest.json` exists; if not, run (or ask Suraj to run):
  `python video_pipeline/ingest.py <recording> --out Own_tasks/taskN`
  Read `ingest/INGEST_REPORT.md`; surface all pipeline warnings up front.

- **Step 1 — Stage A (deterministic validator), first pass.**
  `python video_pipeline/tools/validate_extraction.py Own_tasks/taskN`
  - FAIL ⇒ fix the pipeline output (re-run ingest with adjusted flags, or `--no-stitch`
    fallback) before proceeding. Do not reconstruct on top of a failed extraction.
  - CLEAN/WARN ⇒ proceed; `ingest/VALIDATION.json`'s flagged regions carry forward.

- **Step 1.5 — Auto-label tabs (fast, replaces manual OCR grouping).**
  `python video_pipeline/tools/label_tabs.py Own_tasks/taskN`
  Breadcrumb-strip OCR (evidence panel only, pixel-diff cached) writes
  `tab_label` + authoritative `panel_role` (evidence / form-chrome) into the
  manifest and `ingest/tab_groups.json` = {tab_label: [ordered tiles]}. Groups
  are best-effort (the reconstructor verifies each breadcrumb); use them as the
  dispatch sharding, not gospel.

- **Step 2 — Chrome first (completeness checklist).** Read each `ingest/chrome/*.png`.
  The tab bar enumerates every evidence tab the task has. Transcribe the list —
  it is the completeness contract for Step 6. Cross-check it against the tab_label
  keys in `tab_groups.json`: a tab in the chrome strip with no group means the
  recording opened it but the OCR labeler missed it — reconstruct it from its
  keyframes explicitly.

- **Step 3 — Reconstruct per tab.** Dispatch `doc-reconstructor` — **one per
  `tab_groups.json` group**, in parallel, **≤12 tiles each** (task2 lesson: dense
  academic text can trip a spurious content-filter block; smaller dispatches lower
  that risk). Also dispatch ONE reconstructor for the form panel (the
  `panel_role: form-chrome` right tiles) to capture the question + AI answer +
  Format/Verify line. Per ARCHITECTURE §6 Step 2: Markdown index, LaTeX equations,
  Markdown tables, `[FIGURE:]`, `[UNREADABLE:]` (never guess), `[CONTINUES]` (never
  complete truncated text), char-by-char decisive values with `<!-- src: -->` tags,
  continue-after-text chaining, image before instructions. If a dispatch dies on a
  filter/API error, re-dispatch it on a narrower slice (halve the tiles); if that
  still fails, reconstruct that slice yourself from the keyframes. Write
  `reconstructed/*.md` + `EVIDENCE_INDEX.md`.

- **Step 4 — Stage A, second pass.** Re-run the validator — the reconstruction now
  exists, so the text-quality (A5) and cross-engine OCR tripwire (A7) checks engage.
  FAIL ⇒ repair loop (targeted re-transcription of the failing docs only).

- **Step 5 — Stage B (extraction-evaluator) — THE compulsory evaluation gate.**
  Dispatch `extraction-evaluator` with the task folder path. It audits against the
  BASE VIDEO: mandatory list (all flagged regions + decisive values + markers) plus
  ≥30 random units (C=0 sampling), blind re-transcription + mechanical diff, verdicts
  per checklist with cited evidence.
  - PASS ⇒ proceed.
  - FAIL ⇒ repair loop: fix ONLY the regions in its FINDINGS (with its evidence in
    the repair context), re-run Step 4, re-dispatch the evaluator (fresh random
    sample). Track defect counts per iteration; stop on non-improvement or after
    3 iterations ⇒ escalate to Suraj with the evidence bundle (failing regions,
    extracted frames, diffs) and a concrete ask (re-record stretch X / paste
    screenshot of region Y / confirm immaterial). Never pass a known-defective
    extraction downstream. Log every loop iteration in
    `video_pipeline/learning/LESSONS.md` per EXTRACTION_QA_RULES §7.

- **Step 6 — Completeness gate (BLOCKING, inherits DO_TASK step-1 semantics).**
  Chrome tab list vs reconstructed docs; question + AI answer + Verify line present;
  every remaining `[UNREADABLE]` and warning enumerated. Anything missing ⇒ STOP and
  ask Suraj by name. Suraj may confirm "that's everything the task shows."

- **Step 7 — Hand off to DO_TASK step 1.** Evidence input = `reconstructed/*.md`
  (searchable index) + the image set (ground truth per `EVIDENCE_INDEX.md`). DO_TASK
  runs unchanged — all five agents, all gates; decisive values verified against
  images, never against the Markdown.

- **Step 8 — Close the loop (MANDATORY, after every task).** Dispatch the
  `lessons-scribe` agent with the full gate trace (extraction gates + DO_TASK gates,
  every defect/repair/escalation, any threshold that fired). It appends the
  `video_pipeline/learning/LESSONS.md` entry (with numbers) AND applies the owning
  rule/threshold change in the same session (EXTRACTION_QA_RULES §7). Then produce a
  short **session handoff** (the session-handoff format) so the next session resumes
  without re-deriving state. This step is not optional: the system only improves if
  every task writes its learning. A task is not "done" until Step 8 is written.

## Reporting (Rule 8)

At the end, report the gate chain verbatim, e.g.:
`Stage A: WARN (2 env warnings) → tabs: 6 groups → reconstruction: 6 docs →
Stage A: CLEAN → extraction-evaluator: PASS (34 units, 0 defects) → completeness:
all 7 tabs present → handed to DO_TASK → LESSONS + handoff written.` Never
summarize a gate as "ok" without its numbers.
