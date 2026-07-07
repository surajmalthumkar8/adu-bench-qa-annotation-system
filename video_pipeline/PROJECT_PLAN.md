# PROJECT_PLAN — Video-Ingest Subsystem

One screen recording in, task-ready reconstructed evidence out. This subsystem replaces
manual screenshot pasting as the evidence intake for the ADU-Bench annotation system.

## 1. Problem statement

Today Suraj pastes task content into Claude Code as text plus ~28 individual screenshots
per task (see `Own_tasks/task1/` for a live example). This is:

- **Tedious** — every evidence tab, every scrolled page region, every wide equation must
  be captured, cropped, and pasted by hand.
- **Lossy** — the system's own validation notes
  (`system/learning/VALIDATION_STORM_2026-07-05.md`) rank *incomplete pasted evidence* as
  failure mode #1 ("silently flips verdicts") and *screenshot misreading* as #4. The only
  current mitigation is a BLOCKING completeness gate that stops the task and asks for
  more screenshots — which trades correctness for round-trips.
- **Context-blind** — screenshots taken one at a time lose document continuity: which
  page follows which, which tab a fragment came from, whether an equation was cut off.

## 2. What we build

Input: a single screen recording (mp4, ~60–90 s, possibly longer — see RECORDING_SOP)
of Suraj scrolling through the whole task: question, AI answer, every evidence tab.

Output: `Own_tasks/taskN/ingest/` — stitched full-page images, cropped UI chrome (the
tab bar = the completeness checklist), deduplicated raw keyframes, and a `manifest.json`
describing exactly what was seen, in what order, with what confidence. A Claude-side
workflow (`INGEST_VIDEO`, Phase 2) then reconstructs each document into editable
Markdown and hands off to the existing DO_TASK workflow.

End-user experience:

```
python video_pipeline/ingest.py recording.mp4 --out Own_tasks/task7
# then, in Claude Code:
ingest Own_tasks/task7
```

Everything downstream — the five mandatory agents, the validator, every gate — runs
unchanged.

## 3. Framing corrections (why this is NOT what was first proposed)

The original brief framed this as "reconstruct everything into an editable document,
then solve from the reconstruction." Research (see RESEARCH.md) forced two corrections:

1. **Don't feed the video to a model; feed stitched images.** Video-native LLM ingestion
   (Gemini is the only frontier API that accepts mp4) tokenizes frames at 70–280
   tokens/frame — far below the 1,120+ tokens a high-resolution image gets. Small
   on-screen text does not survive. Local preprocessing (segment → dedup → stitch) into
   high-resolution page images, read as images, is strictly higher fidelity and works
   with any vision model, including Claude in-session.
2. **The reconstruction is an index, not the ground truth.** A pure two-stage design
   (reconstruct → solve from the Markdown) propagates any OCR/transcription error
   straight into the verdict. Adopted principle: **reconstructed Markdown is the
   searchable index; the stitched images remain ground truth.** Decisive values (ISBNs,
   numbers, table cells, option letters) are always verified against the images —
   the same character-by-character protocol DO_TASK already mandates for screenshots.

The problem is also correctly framed as document understanding rather than OCR — but the
hard, novel part turned out to be neither: it is **video → page-image reconstruction**
(scroll stitching), which research confirmed is an unfilled gap in the open-source
ecosystem. Document parsing itself is commoditized and stays pluggable.

## 4. Locked decisions

| Decision | Choice | Rationale |
|---|---|---|
| Parsing backend | **Claude vision, in-session** | No new API keys; annotation task content never leaves the existing Claude channel (platform confidentiality); no GPU required; Claude is already the model doing the task. Pluggable interface keeps MinerU/Gemini available later. |
| Integration | **Feeds DO_TASK** | Reconstruction becomes the evidence-intake stage. All five agents and every quality gate stay intact, including the BLOCKING completeness gate (recording missed a tab ⇒ ask Suraj by name). |
| Hardware | **CPU-only**, Windows 11, Python 3.12 | User's machine has no usable GPU. Preprocessing is ffmpeg + OpenCV, fully CPU-viable. |
| Cost & access | **Zero-cost, zero-exfiltration**: Claude Code + open-source CPU tools only; no external LLM APIs; no Feather/Henna portal login — the recording is the ONLY input | User requirement (2026-07-05). Free decorrelated verifiers (RapidOCR, ffmpeg, OpenCV) cover the QA layer; MCP servers rejected as redundant with Bash (RESEARCH §8). |
| QA gate | **Compulsory two-stage gate** — deterministic validator (Stage A) + extraction-evaluator agent (Stage B) vs the BASE VIDEO, with a bounded repair loop | User requirement (2026-07-05). The base video is the source of truth; no extraction reaches DO_TASK unverified. Rules: `rules/EXTRACTION_QA_RULES.md`. |

## 5. Goals

1. Zero manual screenshots for a standard task: one recording covers everything.
2. Fidelity ≥ the manual-screenshot baseline: every decisive value legible in the
   output images; equations, tables, and figures represented in the reconstruction.
3. **Never silently drop content.** Any stitching failure degrades to overlapping raw
   keyframes with a flag — worst case equals today's workflow, never worse.
4. The completeness gate survives: the system detects (via the recorded tab bar) which
   evidence tabs exist and blocks if any were never opened in the recording.
5. Reusable core: the pipeline knows nothing about ADU-Bench; a thin workflow adapts it.

## 6. Non-goals

- No browser automation of Henna/Feather (root `ARCHITECTURE.md` non-goal stands —
  Suraj records by hand).
- No external OCR/parsing APIs and no local GPU models in the MVP (pluggable later,
  Phase 4).
- No horizontal scroll stitching in the MVP (flagged and emitted as raw keyframes).
- No audio processing; the recording is treated as silent pixels.
- No real-time processing; this is a batch tool run after recording.

## 7. Success criteria / acceptance

- **A1 (kill-risk, tested FIRST):** decisive characters (ISBN digits, table cells) in
  produced tiles are correctly legible when read by Claude's Read tool. If this fails at
  realistic recording settings, the architecture must be revisited before any further
  build-out (see ROADMAP Phase 1).
- **A2 (MVP acceptance):** re-record task1 — whose ground truth is the 28 hand-taken
  screenshots and completed `Own_tasks/task1/task_1.md` — and the pipeline's
  reconstruction must contain every piece of evidence the manual paste contained, with
  matching decisive values.
- **A3:** coverage invariant holds on every run: every deduplicated keyframe is
  represented in at least one output image (enforced in code, exit non-zero otherwise).
- **A4:** synthetic golden tests (rendered tall page → generated scroll video → stitch →
  SSIM vs original) pass, including injected sticky headers, blur, and page-snaps.
- **A5:** the compulsory QA gate is exercised end-to-end on a real task: Stage A
  validator CLEAN/WARN, extraction-evaluator PASS with a logged ≥30-unit C=0 sample,
  and at least one seeded-defect drill (deliberately corrupt a tile/transcription and
  confirm the gate catches it — a gate that has never caught anything is untested).

## 8. Deliverables map

| Doc | Contents |
|---|---|
| `ARCHITECTURE.md` (this dir) | Full pipeline design, manifest schema, failure-mode table, Claude-side workflow spec, module layout, CLI, dependencies |
| `RESEARCH.md` | Cited ecosystem survey, comparisons, assumption challenges |
| `ROADMAP.md` | Phases 0–4, risk register |
| `RECORDING_SOP.md` | How to record so the pipeline can succeed |

Implementation begins only after these docs are reviewed (ROADMAP Phase 0).
