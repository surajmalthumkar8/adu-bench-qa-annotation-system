# ROADMAP — Video-Ingest Subsystem

Phases are strictly ordered; each has an exit criterion.

**Status 2026-07-05 — QA layer built ahead of the pipeline (user directive):**
the compulsory extraction QA gate now exists and is smoke-tested —
`rules/EXTRACTION_QA_RULES.md`, `tools/validate_extraction.py` (Stage A, verified on
negative + synthetic-positive fixtures), `.claude/agents/extraction-evaluator.md`
(Stage B), `system/workflows/INGEST_VIDEO.md` (gate chain wired), `learning/LESSONS.md`
(learning loop seeded), `requirements.txt`. Binding constraints added: zero-cost
(Claude Code + open-source CPU tools only, no external LLM APIs), no portal login.
Remaining build order below.

## Phase 0 — Scaffold & test harness (tests before stitcher)

- Create `video_pipeline/src/` module skeleton, `config.py` (IngestConfig dataclass),
  `requirements.txt`, `ingest.py` argparse shell.
- Build `tests/synth.py`: render a tall synthetic page (text + Markdown table + LaTeX
  equation image), programmatically generate scroll videos from it — plain scroll,
  plus injected sticky header, motion blur, and page-snap variants.
- Golden-test scaffolding: stitch a synthetic video, assert SSIM vs the source image.

**Exit:** synthetic videos generate deterministically; test suite runs (stitch tests
red, everything else green).

## Phase 1 — MVP: single-document vertical scroll

**Run the kill-risk experiment FIRST (A1):** record a real document page at the
RECORDING_SOP settings (CRF ≤16, I444 — see SOP hard requirement 0), produce tiles by
hand at the ARCHITECTURE §2.8 geometry (≤2000 px both sides, ≤4,784 visual tokens),
and have Claude's Read tool transcribe decisive characters (ISBN digits, table cells,
superscripts). Also verify empirically that ≤2000 px images pass through the Read tool
untouched (RESEARCH §7 caveat). If characters are not reliably legible, revisit tile
geometry / recording resolution / the whole approach **before** building further. This
risk can invalidate the architecture faster than any stitching bug.

Then build the end-to-end path:
- `probe.py` → `frames.py` (full decode + displacement-budget frame selection,
  ARCHITECTURE §2.2) → motion-aware `dedup.py` (dy≈0 AND pHash≤2;
  last-frame-of-dwell selection; dwell_ms recorded) → fixed-crop sticky handling
  (config value; auto-detect deferred) → `stitch.py` (3-strip matchTemplate median dy +
  phaseCorrelate cross-check, corr ≥ 0.95 with whitespace-strip fallback, integer-only
  compositing, whitespace-row seam cuts, failure-mode classification per ARCHITECTURE
  §2.6–2.7) → `tiler.py` (content-column crop; ≤2000 px / ≤4,784-token tiles;
  whitespace-boundary cuts; 2–4-line overlap; text-size gate with Lanczos upscale) →
  `manifest.py` → `coverage.py` hard gate → `report.py`.
- CLI complete incl. `--no-stitch` fallback and exit codes 0/1/2.

**Exit (A2):** re-record task1 (ground truth: 28 hand screenshots +
`Own_tasks/task1/task_1.md`); the pipeline output contains every piece of evidence the
manual paste contained, decisive values legible and matching. Coverage invariant (A3)
and synthetic goldens (A4) green.

## Phase 2 — Multi-tab / multi-doc + Claude workflow

- Tab-bar-region pHash change detector in `segment.py` (primary boundary signal),
  AdaptiveDetector as secondary; chrome extraction to `chrome/`.
- ~~Write `system/workflows/INGEST_VIDEO.md`~~ DONE (incl. compulsory QA gate chain).
- ~~Add the routing row to `CLAUDE.md`~~ DONE.
- Write `.claude/agents/doc-reconstructor.md` (`model: opus`).
- Extend DO_TASK step 1 to accept "reconstructed evidence" as an input form (decisive
  values verified against images per `EVIDENCE_INDEX.md`).
- Per-segment parallel reconstruction; completeness gate wired to the chrome tab list.
- **QA-gate live drill (acceptance A5):** run the full gate chain on a real task,
  including a seeded-defect drill — deliberately corrupt one tile and one transcription
  value; the gate must catch both. Log the drill in `learning/LESSONS.md`.

**Exit:** a full multi-tab task goes recording → ingest → Stage A → reconstruction →
Stage A → extraction-evaluator PASS → DO_TASK → deliverable with zero manual
screenshots; the completeness gate correctly blocks when a tab is deliberately omitted
from a test recording; the seeded-defect drill passes.

## Phase 3 — Hardening

- Auto sticky-band detection (row-motion profile) replaces fixed crop.
- Zoom / horizontal-scroll / PDF page-snap guards exercised on real recordings.
- Seam validation (re-match + SSIM across every seam; demote failures to raw frames).
- Dynamic-region masking (caret blink, animations) + transient-overlay aux keyframes.
- Optional document anchoring: Tesseract pass per tile, injected into transcription
  prompts as "noisy reference — trust the image" (olmOCR's biggest published
  anti-hallucination lever, RESEARCH §6).
- Threshold tuning (displacement budget, min-corr, dedup pHash distance) from a corpus
  of real task recordings; every new failure becomes a synthetic regression test.
- Finalize RECORDING_SOP.md from what actually broke.

**Exit:** N consecutive real tasks (suggest N=5) ingest cleanly with zero
manual-screenshot fallbacks and zero reviewer-visible evidence errors.

## Phase 4 — Pluggable parser backends (optional, demand-driven)

Only if Phase 1–3 experience shows in-session reconstruction fidelity or token cost is
a problem:
- `ParserBackend` protocol (ARCHITECTURE §9); `ClaudeInSession` default.
- Candidate adapters, in preference order given constraints at that time:
  MinerU (best open math/tables; needs ~8GB VRAM) · dots.ocr (MIT, 3B) ·
  Gemini Flash (API — requires revisiting the confidentiality decision).
- Re-check leaderboards first (RESEARCH §5 — the space moves fast).

**Exit:** backend swap requires zero changes to pipeline, manifest schema, or DO_TASK.

## Risk register

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | **Legibility ceiling** — Claude Code clamps images to 2000×2000 px; small characters unreadable at input | Kills the approach | A1 experiment first thing in Phase 1; §2.8 tile geometry (column crop, ≤2000 px, ≤4,784 tokens, text-size gate + Lanczos upscale); RECORDING_SOP req 0 (CRF≤16, I444) + ≥1440p |
| R2 | **Horizontally clipped content** — wide equations behind inner h-scrollbars never shown in the video (observed in task1 screenshots) | Wrong/incomplete evidence | SOP: drag every inner h-scrollbar fully right; Claude flags truncated equations and asks |
| R3 | Hash-only dedup eats slow smooth scroll | Silent content loss | Motion-aware dedup is mandatory (dy≈0 AND pHash≤2), not an optimization |
| R4 | Scene-detector false cuts on scrolling (documented ContentDetector failure case) | Fragmented segments | Tab-bar signal primary; dy-residual secondary; ContentDetector avoided; tuned on synthetics + real clips |
| R5 | Token cost: ~30–60 images/task at ~3.2–4.8k visual tokens each | Cost/context pressure | doc-reconstructor subagent isolation, ≤15–25 tiles per subagent; correctness over speed is the project contract |
| R6 | Fast scrolling → insufficient stitch overlap + blur | Quality | Displacement-budget frame selection guarantees ~60% overlap at any speed; last-frame-of-dwell defeats residual blur; SOP recommends 2–3 min recordings |
| R7 | Recorder burns in cursor/click-highlight overlays that corrupt strip matching | Stitch confidence drops | 3-strip median dy + dynamic-region masking; verify Suraj's recorder settings (SOP open question) |
| R8 | Reconstruction drift/hallucination (paraphrase, plausible completion, digit substitution) | Verdict risk | Index-vs-ground-truth principle; `[CONTINUES]`/`[UNREADABLE]` abstention rules; decorrelated zoomed-crop spot-checks (disagreement ⇒ abstain, never coin-flip); optional Tesseract anchoring (Phase 3); DO_TASK char-by-char protocol against images |
| R9 | Default recorder settings (4:2:0 chroma, high compression) silently degrade text before the pipeline ever runs | High — undermines everything downstream | RECORDING_SOP hard requirement 0 (CRF≤16, I444, full range, native res); CLI warns on low-bitrate/4:2:0 input via ffprobe |
| R10 | Generative enhancement rewrites evidence (SR models hallucinate glyphs) | Catastrophic if introduced | Explicit ban in ARCHITECTURE §2.4 — only non-generative Lanczos resampling permitted |
| R11 | Evaluator self-preference (Claude judging Claude skews lenient — measured, survives anonymization) | False PASS at the gate | Perception-not-preference protocol: blind re-transcription + mechanical diff; checklist verdicts with cited evidence; C=0 sampling floor (EXTRACTION_QA_RULES §2–3) |
| R12 | Repair loop oscillates or degrades the extraction | Wasted cycles / regression | Max 3 targeted iterations, monotone-improvement requirement, keep best-ever, escalate with evidence (EXTRACTION_QA_RULES §5) |
| R13 | QA gate that never fires is untested (silent blind spots) | Unknown gate reliability | Seeded-defect drill is part of Phase 2 acceptance (A5); every real failure feeds learning/LESSONS.md (Rule 7) |

## Open questions (carried into Phase 0 review)

1. Recording length: is 2–3 min acceptable instead of 60–90 s? (Recommended: yes.)
2. Does Suraj's screen recorder add cursor-highlight overlays? Full-window capture
   including the question/answer panel? (Both required answers for RECORDING_SOP.)
3. Where reconstruction lives: proposed `Own_tasks/taskN/reconstructed/` (auditable
   files) vs chat-context only. Recommended: files.
