# ARCHITECTURE — Video-Ingest Subsystem

Scope: this document covers only the video-ingest subsystem. The annotation system's
architecture lives in the repo root `ARCHITECTURE.md`.

Design principle (load-bearing, referenced throughout): **reconstructed Markdown is a
searchable index; stitched images are ground truth.** Decisive values are verified
against images, never against the reconstruction.

## 0. Shape of the system

```
recording.mp4
   │  local Python, CPU-only
   ▼
[probe] → [extract frames] → [segment] → [dedup] → [sticky crop] → [stitch] → [tile]
   │                                                                            │
   └────────────────────────────► manifest.json + coverage gate ◄───────────────┘
                                        │
                                        ▼  Claude Code, in-session
                     INGEST_VIDEO workflow: Stage A validator (deterministic)
                     → chrome-first completeness checklist → per-segment
                     reconstruction (doc-reconstructor subagent) → Stage A re-run
                     → Stage B extraction-evaluator vs BASE VIDEO (compulsory, §10)
                     → BLOCKING completeness gate → hand off to DO_TASK step 1
```

Two halves, one contract: the Python pipeline emits images + `manifest.json`; the
Claude workflow consumes them. Neither half knows the other's internals.

## 1. Directory / module layout

```
video_pipeline/
  PROJECT_PLAN.md  ARCHITECTURE.md  RESEARCH.md  ROADMAP.md  RECORDING_SOP.md
  requirements.txt
  rules/
    EXTRACTION_QA_RULES.md binding rules for the compulsory QA gate (§10)
  learning/
    LESSONS.md             append-only learning loop (QA failures ⇒ rule updates)
  tools/
    validate_extraction.py Stage-A deterministic validator (built, tested)
  ingest.py                CLI entrypoint (thin argparse wrapper over src/)
  src/
    __init__.py
    config.py              IngestConfig dataclass — every tunable in one place
    probe.py               ffprobe metadata (resolution, fps, duration)
    frames.py              full decode (imageio-ffmpeg) + displacement-budget selection
    segment.py             tab/document-switch segmentation (two signals, §2.3)
    dedup.py               motion-aware perceptual-hash dedup + last-frame-of-dwell pick
    sticky.py              sticky header/footer band detection + chrome extraction
    stitch.py              scroll-offset estimation + confidence + compositing
    tiler.py               slice composites into bounded-height overlapping tiles
    manifest.py            manifest schema (dataclasses), writer, validation
    coverage.py            coverage invariant + seam validation (never-drop enforcer)
    report.py              INGEST_REPORT.md generator
  tests/
    synth.py               synthetic scroll-video generator (golden-test harness)
    test_stitch.py  test_segment.py  test_dedup.py  test_coverage.py
```

Per-task output convention (task folder stays self-contained, like today):

```
Own_tasks/taskN/
  recording.mp4                 input, kept
  ingest/                       machine-written, regenerable (--force to overwrite)
    manifest.json
    INGEST_REPORT.md            human/Claude-readable summary + warnings
    chrome/   segNN_chrome.png  cropped sticky bands — the tab bar IS the
                                completeness checklist
    pages/    segNN_tileMM.png  stitched composite tiles
    keyframes/ fNNNNNN.png      deduped raw keyframes (ground-truth fallback, kept)
    debug/                      seam visualizations, correlation logs (--debug only)
  reconstructed/                Claude-written by INGEST_VIDEO (Phase 2)
    question.md  answer.md  doc1.md  doc2.md ...
    EVIDENCE_INDEX.md           DocN Page Y → image file map
```

## 2. Pipeline stages

### 2.1 Probe (`probe.py`)
ffprobe: resolution, fps, duration. Warn (do not fail) below 1920 px width —
legibility floor; RECORDING_SOP asks for ≥ 1440p.

### 2.2 Extract + select (`frames.py`) — displacement-budget, not fixed-rate
Decode **all** frames (a 60–90 s clip is only ~2,700 frames at 30 fps — cheap on CPU),
compute inter-frame `dy` via phase correlation on 4×-downsampled grayscale, then select
frames by **accumulated-displacement budget**: one frame per ~35–40% of viewport height
of scroll (guaranteeing ~60% stitch overlap at any scroll speed) plus the
last-frame-of-each-dwell (§2.4). Working PNGs go to `ingest/.work/` (deleted on
success unless `--debug`).

Rationale (RESEARCH §5): fixed-rate sampling has a dual failure mode — at fast scroll
it can leave insufficient overlap for stitching; during dwell it wastes frames. The
full-decode dy signal also powers segmentation (§2.3) and dedup (§2.4) for free.

### 2.3 Segment (`segment.py`) — two signals
1. **Tab-bar-region change detector (PRIMARY)** — this UI's killer feature. The Henna
   evidence panel has a sticky tab strip (`Doc1 P34-37 · Doc2 P153-155 | PDF`) whose
   highlight state changes exactly on tab switch. pHash the top band per frame; a
   band-hash jump is a definitive boundary — it also catches switches between visually
   similar docs that pixel-difference detectors miss.
2. **dy-residual detector (SECONDARY)** — a frame pair whose global translation model
   fails (large non-translational residual, dy undefined) is a page/tab/window change.
   PySceneDetect `AdaptiveDetector` (rolling-average threshold) may back this up, but
   plain `ContentDetector` is explicitly avoided: sustained scrolling mimics its
   camera-motion failure case and false-triggers (RESEARCH §5).

Either signal alone opens a boundary; agreement raises `boundary_signal` confidence in
the manifest. Segments are temporal, content-agnostic: the pipeline never guesses what
a segment *is* (see `content_hint`, §3).

### 2.4 Dedup (`dedup.py`) — motion-aware, not hash-only
Within a segment, drop frame N+1 only if **estimated scroll dy ≈ 0 AND pHash distance
≤ 2** (static dwell). Never dedup during motion, even at near-identical hashes — slow
smooth scroll produces hash-similar frames that each reveal new content; hash-only
dedup would eat it. From each static run keep the **last frame of the dwell**: H.264
encoders progressively refine static content across P-frames after motion stops, so
the latest dwell frame is the cleanest. (Variance-of-Laplacian "sharpest frame" was
rejected — codec ringing/mosquito noise *inflates* Laplacian variance, so VoL can
prefer the most artifacted frame; RESEARCH §5.) Record each dwell's duration — it is
an importance signal (`dwell_ms` in the manifest, §3).

**Banned technique:** no generative super-resolution anywhere in the pipeline
(Real-ESRGAN, BasicVSR++, diffusion SR). These models hallucinate plausible-looking
glyphs — in an evidence-verification system they can silently rewrite the evidence
(RESEARCH §5). Only non-generative resampling (Lanczos) is permitted, and only
upscaling (§2.8).

### 2.5 Sticky detection + crop (`sticky.py`)
Per segment, take frame pairs with confirmed global motion; compute per-row absolute
difference. Contiguous top/bottom bands with near-zero change while the middle moves =
sticky chrome (tab bar, doc/page header, question-panel header). Crop the band from all
frames before stitching; save one representative copy as `chrome/segNN_chrome.png` —
it is *evidence* (the completeness contract), not noise. MVP may use a fixed-crop
config value; auto-detection is Phase 3.

### 2.6 Scroll-offset estimation (`stitch.py`)
Per consecutive keyframe pair, grayscale both, then:

- `cv2.matchTemplate(TM_CCOEFF_NORMED)` of **three** horizontal strips (~150 px each,
  at different heights of frame N+1) against frame N; take the **median dy** — robust
  to cursor/highlight occlusion corrupting any single strip; discard per-strip
  correlation outliers.
- Cross-check with `cv2.phaseCorrelate` (sub-pixel global translation).

Two guards learned from production long-screenshot tools (RESEARCH §5):
- **Low-variance (whitespace) strips destabilize `TM_CCOEFF_NORMED`** — the corr gate
  would fail on legitimate alignments over empty page regions. Detect low-variance
  strips and widen the template or fall back to the accumulated per-frame dy.
- **Dynamic regions corrupt matching** — blinking text cursor, hover effects,
  animations, lazy-loading images. Mask high-temporal-variance regions before matching;
  transient overlay content (tooltips, popovers, dropdowns) that stitching would
  destroy is emitted as auxiliary keyframes flagged `transient_overlay` (§3).

Classification:

| Observation | Verdict | Action |
|---|---|---|
| dy > 0, dx ≈ 0, corr ≥ 0.95, \|dy_tm − dy_pc\| ≤ 2 px | scroll | stitch |
| dy ≈ dx ≈ 0 | static | (already deduped) |
| dx ≠ 0 | horizontal scroll | no h-stitch in MVP: emit both frames as raw keyframes, flag `horizontal_scroll` |
| overlap < min_overlap, or corr low but multi-scale resize matches | page-snap / zoom | close composite, start new one, flag — a page boundary is a break, not an error |
| corr low, unclassifiable | break | close composite; emit both boundary frames raw, flag `low_confidence_seam` |

### 2.7 Composite — integer offsets, whitespace seams, hard cuts
- **Integer pixel offsets only.** Sub-pixel warping resamples and blurs 1-px font
  strokes; `phaseCorrelate`'s sub-pixel value validates the integer dy, never warps.
- **Hard cuts, no blending.** Blending exists to hide exposure/parallax differences
  screen content doesn't have; any blend across a ≥1 px misalignment ghosts glyphs.
- **Place the cut on a whitespace row**: within the overlap, choose the row of minimum
  ink/variance so residual off-by-one errors land between text lines, never through
  them. (Also absorbs the 1-px non-integer offsets of fractional-DPI/125%-zoom
  sessions.)

Record every seam (y-position, correlation, dy agreement) in the manifest.

### 2.8 Tile (`tiler.py`) — geometry is dictated by Claude's input limits
Verified constraints (RESEARCH §6): Claude Code's Read tool clamps images to
**2000×2000 px** before they reach the model; the API charges
`⌈w/28⌉ × ⌈h/28⌉` visual tokens with a **4,784-token cap** on the high-resolution tier
(server-downscales above it). A 2560-wide tile would be silently clamped to 2000 px —
a 22% linear resolution loss on every tile. Therefore:

1. **Crop to content-column width first** (never downscale). A 2560-wide stitch whose
   text column is ~1400 px is cropped to the column: text stays at native scale and
   tiles get taller per token. Genuinely wide content (tables) splits into left/right
   halves sharing a key column — split, don't shrink.
2. **Tile ceiling: ≤2000 px on BOTH sides AND ≤4,784 visual tokens** (e.g. 2000×1848,
   or 1400-wide × 2000-tall at 3,600 tokens). Never rely on server/Read-tool resizing.
3. **Cut tile boundaries on whitespace rows** (same row-ink profile as §2.7) so no
   text line is ever split; overlap = **2–4 text lines (~100–200 px)**, not a blind
   percentage — enough for seam-merging, no wasted token budget.
4. **Text-size gate:** estimate body-text x-height per composite (row-ink profile
   periodicity). Decisive text must be ≥15–20 px tall at final input — VLM OCR
   accuracy cliffs below ~8 px/char (RESEARCH §6). If source text is smaller, upscale
   the tile 1.5–2× with **Lanczos** (non-generative) before writing, keeping the
   ≤2000 px / ≤4,784-token ceiling by slicing more tiles.

Full strips optionally kept in `debug/` only.

### 2.9 Verify & write (`coverage.py`, `manifest.py`, `report.py`)
Coverage invariant (§5), `manifest.json`, `INGEST_REPORT.md`.
Exit codes: **0** clean · **2** completed-with-warnings · **1** failure.

## 3. manifest.json schema (the pipeline↔Claude contract)

```json
{
  "schema_version": 1,
  "source": {"video": "recording.mp4", "duration_s": 74.2,
             "resolution": [2560, 1440], "decoded_frames": 2226,
             "created": "2026-07-05T18:30:00"},
  "config": {"displacement_budget": 0.35, "min_stitch_corr": 0.95,
             "max_tile_px": 2000, "min_text_px": 15},
  "segments": [
    {
      "id": "seg01",
      "time_range_s": [0.0, 11.5],
      "frame_range": [0, 46],
      "boundary_signal": "tab_bar_change|scene_detect|start|end",
      "chrome_image": "chrome/seg01_chrome.png",
      "sticky_bands_px": {"top": 128, "bottom": 0},
      "content_hint": null,
      "outputs": [
        {"type": "stitched_tile", "path": "pages/seg01_tile01.png", "order": 1,
         "source_frames": [0, 4, 9, 14], "source_times_s": [0.0, 1.0, 2.25, 3.5],
         "composite_id": "seg01_c1", "tile_y_range": [0, 1600],
         "seams": [{"y": 812, "corr": 0.991, "dy_agreement_px": 0}],
         "stitch_confidence": 0.991,
         "dwell_ms": [1500, 800, 2200],
         "est_text_px_height": 18, "upscaled": 1.0,
         "flags": []},
        {"type": "raw_keyframe", "path": "keyframes/f000031.png", "order": 4,
         "source_frames": [31], "source_times_s": [7.75],
         "flags": ["horizontal_scroll", "overlaps_previous"]},
        {"type": "aux_keyframe", "path": "keyframes/f000038.png", "order": 5,
         "source_frames": [38], "source_times_s": [9.5],
         "anchor_tile": "pages/seg01_tile02.png", "anchor_y": 430,
         "flags": ["transient_overlay"]}
      ]
    }
  ],
  "coverage": {"kept_keyframes": 41, "represented_in_outputs": 41, "orphans": 0},
  "warnings": ["seg03: 2 low-confidence seams — emitted overlapping raw keyframes"]
}
```

Notes:
- `content_hint` is **always null at pipeline level**. Document identity (question /
  AI answer / Doc1 / Doc2 / PDF reference) is assigned by Claude in the workflow, never
  by CV code. The pipeline only knows "visually distinct segments in temporal order."
- `outputs[].order` is the reading order within a segment; segments are ordered by time.
- Every output carries `source_frames` — this is what the coverage gate checks.
- **Salience signals kept, not discarded** (RESEARCH §5): `dwell_ms` per stitched
  region (long dwell = the human read it — a prioritization hint for reconstruction),
  and `aux_keyframe` outputs preserve transient overlay content (tooltips, popovers,
  expanded dropdowns) that stitching would otherwise destroy, anchored to their
  position in the stitched page.
- `est_text_px_height` + `upscaled` let the workflow know whether the text-size gate
  (§2.8) fired and how trustworthy small print is.

## 4. Failure-mode handling (stitcher)

Universal fallback: **degrade to overlapping un-stitched keyframes with a flag.**
Worst case, the output equals today's manual-screenshot workflow — never worse, never
silent.

| Failure mode | Detection | Response |
|---|---|---|
| Sticky header / tab bar / navbar | Row-motion profile: rows static while body moves | Crop before stitch; band saved to `chrome/` |
| Smooth-scroll motion blur | dy signal identifies dwell periods | Last-frame-of-dwell selection; blurred mid-scroll frames skipped when a clean neighbor covers the content |
| Cursor / hover-highlight occlusion | Single-strip match corrupted | 3 strips, median dy; per-strip corr outliers discarded |
| Whitespace at the joint | Low-variance strip → unstable TM_CCOEFF_NORMED score | Widen template or fall back to accumulated per-frame dy — don't fail the corr gate on empty regions |
| Dynamic content (blinking caret, animations, lazy-load) | High temporal variance in a static-dy region | Mask before matching; tooltips/popovers emitted as `aux_keyframe` with `transient_overlay` flag |
| PDF page-snap viewer | Overlap below min, or corr collapse at large dy | Close composite, start new one (natural break) |
| Zoom | matchTemplate fails, multi-scale resize match succeeds | Flag `zoom_detected`, break composite, emit raw keyframes for the zoomed stretch |
| Horizontal scroll (real in this UI — wide equations have inner h-scrollbars) | dx ≠ 0 from phaseCorrelate | MVP: emit both frames raw with `horizontal_scroll`; Claude reads both |
| Anything else (low-confidence seam) | corr < 0.95 or dy disagreement > 2 px | Close composite; emit both boundary frames raw, flag; manifest warning |

## 5. Quality / verification strategy

- **Coverage invariant (code, hard gate):** every deduped keyframe id appears in ≥ 1
  output's `source_frames`. `coverage.py` auto-promotes orphans to `raw_keyframe`
  outputs and records the promotion; if that fails, exit 1. Silent content loss is
  structurally impossible.
- **Seam validation (code):** for each seam, re-match a strip *spanning* the seam of
  the composite back against the original source frame; SSIM (a ~15-line numpy/cv2
  helper — no scikit-image dependency) over the overlap must clear a threshold, else
  that composite region is demoted to raw keyframes.
- **Synthetic golden tests:** `tests/synth.py` renders a tall text+table+equation image,
  programmatically generates scroll videos (with injected sticky headers, blur,
  page-snaps), stitches, asserts SSIM vs the original. Regression suite for every
  hardening phase.
- **Claude-side:** chrome-derived tab list = completeness checklist; spot-check step
  (§6.4); `[UNREADABLE]` is never guessed — ask Suraj, same rule as today; DO_TASK's
  character-by-character protocol runs against images, so a Markdown reconstruction
  error cannot decide a verdict.
- **First real validation:** task1 has 28 hand-taken screenshots + a completed
  submission. Record that same task once; diff the reconstruction against the
  known-good paste. This is the MVP acceptance test (ROADMAP A2).

## 6. Claude-side workflow — `system/workflows/INGEST_VIDEO.md` (CREATED)

The workflow file now exists at `system/workflows/INGEST_VIDEO.md` (routing row added
to `CLAUDE.md`), including the **compulsory QA gate chain** (§10). Still pending:
`.claude/agents/doc-reconstructor.md` (`model: opus` — bulky image reading happens in
subagent contexts, mirroring the evidence-hunter isolation rationale). The
`extraction-evaluator` agent exists at `.claude/agents/extraction-evaluator.md`.

Trigger: Suraj types `ingest Own_tasks/taskN` (the CLI prints this exact line).

- **Step 0 — Precondition.** `ingest/manifest.json` exists and `coverage.orphans == 0`;
  else point Suraj to the CLI / report the pipeline error verbatim. Read
  `INGEST_REPORT.md`; surface all warnings up front.
- **Step 1 — Chrome first (completeness checklist).** Read each `chrome/*.png`. The tab
  bar enumerates every evidence tab the task has. Transcribe that list — it is the
  completeness contract for Step 5.
- **Step 2 — Reconstruct per segment.** Dispatch `doc-reconstructor`, one per segment,
  in parallel; **cap each subagent at ~15–25 tiles** (a max-geometry tile costs
  ~3.2–4.8k visual tokens; the transcription output for dense pages can exceed the
  image tokens — shard long documents across subagents rather than approaching the
  context ceiling). Input: the segment's tiles + raw/aux keyframes in `order`. Output:
  Markdown with headings/paragraphs preserved, equations as LaTeX, tables as Markdown
  tables, figures as `[FIGURE: description]`, per-page provenance headers copied
  verbatim (e.g. `Doc1: 9789812386342.pdf — Page 38`).

  Transcription discipline (anti-hallucination rules, RESEARCH §6 — all published,
  cited):
  - **One tile per read, sequentially, image before instructions.** Feed the previous
    tile's last transcribed lines as a text anchor with "continue after this exact
    text; do not re-emit it" — more reliable than visually detecting the seam, and it
    doubles as an olmOCR-style anchor.
  - **Never complete truncated text.** Words/sentences cut at a tile edge are emitted
    as `[CONTINUES]`, resolved only when the next tile confirms them. Plausible
    continuation is the #1 documented VLM OCR failure mode.
  - decisive-looking values (ISBNs, years, table cells, option letters) transcribed
    character-by-character with an inline provenance tag
    `<!-- src: pages/seg01_tile02.png -->`;
  - anything illegible → `[UNREADABLE: region description, seg01_tile03.png]` — never
    inferred; abstention is explicitly instructed as preferred over inference;
  - outputs flagged `horizontal_scroll` / `low_confidence_seam` / `transient_overlay`
    read extra carefully, all overlapping frames; `dwell_ms` marks the regions the
    human studied longest — prioritize care there;
  - optional hardening (Phase 3): a cheap classical OCR pass (Tesseract) injected into
    the prompt as "noisy reference — trust the image over this text" (document
    anchoring, olmOCR's single biggest anti-hallucination lever).
- **Step 3 — Identify roles.** From headers and layout: which segment is the question +
  AI answer (+ Format/Verify/Tags line), which are DocN evidence tabs, which is the PDF
  reference. Write `reconstructed/*.md` + `EVIDENCE_INDEX.md` (DocN Page Y → files).
- **Step 4 — Spot-check (anti-drift) via DECORRELATED views.** For each decisive value,
  the orchestrator re-reads a **zoomed crop of the raw keyframe** (different geometry =
  decorrelated errors — same-view same-model re-reads make correlated mistakes and are
  weak verification; RESEARCH §6). Agreement ⇒ confirmed. Disagreement ⇒
  `[UNREADABLE]`/escalate to Suraj — never a coin flip between the two readings.
  A crop-and-zoom re-read is also the mandated fallback for any value whose tile has
  `est_text_px_height` below the gate.
- **Step 5 — Completeness gate (BLOCKING, inherits DO_TASK step-1 semantics).** Compare
  the chrome tab list vs segments reconstructed; confirm question + AI answer + Verify
  line present; list every `[UNREADABLE]` and unresolved warning. Anything missing ⇒
  STOP and ask Suraj by name ("the recording never opens Doc2 P153-155 — please
  re-record that tab or paste a screenshot"). Suraj may confirm "that's everything the
  task shows."
- **Step 6 — Hand off to DO_TASK step 1.** Evidence input = `reconstructed/*.md` as the
  searchable index PLUS the image set as ground truth. DO_TASK runs unchanged, all five
  agents, with one addition to its screenshot protocol: for decisive values, the
  evidence-hunter and independent-solver verify against the images listed in
  `EVIDENCE_INDEX.md`, not the reconstructed Markdown.

## 7. CLI

```
python video_pipeline/ingest.py recording.mp4 --out Own_tasks/task7
  --displacement-budget 0.35  frames selected per fraction of viewport scrolled
  --max-tile-px 2000          tile ceiling, both sides (Claude Code Read clamp)
  --min-text-px 15            text-size gate; below ⇒ Lanczos upscale
  --min-corr 0.95             stitch confidence gate
  --no-stitch             keyframes-only fallback (segment + dedup, skip stitching)
  --force                 overwrite an existing ingest/
  --debug                 keep debug/ seam visualizations + work frames
```

Prints a summary (segments, tiles, warnings) and ends with the exact line to paste:
`Done. In Claude Code, run:  ingest Own_tasks/task7`.
`pathlib` throughout (Windows paths). Exit codes per §2.9.

## 8. Dependencies (`requirements.txt` — CPU-only, Windows, Python 3.12)

- `opencv-python` — matchTemplate, phaseCorrelate, Laplacian, compositing
- `scenedetect[opencv]` — ContentDetector/HashDetector
- `imagehash` — pHash (pulls Pillow, numpy, PyWavelets, scipy)
- `imageio-ffmpeg` — **bundles an ffmpeg binary**: setup is `pip install -r
  requirements.txt`, no separate ffmpeg install on Windows
- `Pillow`, `numpy` — explicit pins
- `rapidocr` — Apache-2.0 ONNX OCR, CPU-only: the QA layer's decorrelated
  cross-engine tripwire (§10, check A7)

Nothing else. No scikit-image (SSIM is hand-rolled), no torch. Optional extras
(documented in requirements.txt, not installed by default): Tesseract 5 +
`pytesseract` (second decorrelated engine, per-word confidence; also Phase 3
document anchoring), `rapid_latex_ocr` (coarse equation cross-check). **No MCP
servers** — inside Claude Code, Bash + Python already give full ffmpeg/OCR/imaging
control; MCP wrappers add config surface, not capability (RESEARCH §8).

## 10. Compulsory QA layer — evaluate + validate against the base video

**The base video is the source of truth.** No extraction reaches DO_TASK without
passing this layer. Binding rules: `rules/EXTRACTION_QA_RULES.md`. Research basis:
RESEARCH §7 (methodology) + §8 (free tooling). Design principle: composed,
decorrelated signals — no single check certifies fidelity, but the stack bounds it.

```
              ┌── Stage A: deterministic validator (Python, mechanical) ──┐
extraction →  │ A1 manifest schema + file existence                      │
              │ A2 coverage invariant (every keyframe represented)        │
              │ A3 composite height accounting                            │
              │ A4 tile geometry (≤2000px) + text-size gate               │
              │ A5 text-quality proxies (lexicon, entropy, repetition)    │
              │ A6 CV line-count reconciliation (morphological)           │
              │ A7 cross-engine OCR tripwire (RapidOCR vs reconstruction) │
              │ A8 recording preflight (pix_fmt/resolution via ffprobe)   │
              └──── CLEAN/WARN → Stage B; FAIL → repair loop ─────────────┘
              ┌── Stage B: extraction-evaluator agent (Claude vision) ────┐
              │ audits vs BASE VIDEO frames (ffmpeg -ss exact-frame)      │
              │ blind re-transcription → mechanical diff (anti-self-bias) │
              │ mandatory list (all flags/decisive values/markers)        │
              │ + ≥30 random units, C=0 acceptance sampling               │
              │ checklist verdicts with cited evidence, never scores      │
              └──── PASS → completeness gate → DO_TASK; FAIL → loop ──────┘
Repair loop:  targeted regions only · max 3 iterations · monotone improvement
              · keep best-ever · escalate to Suraj with evidence on exhaustion
```

Key design facts (all cited in RESEARCH §7–8):
- **Perception, not preference**: the evaluator never opines on the reconstruction;
  it independently transcribes source regions blind, then a mechanical diff decides —
  the strongest available mitigation for same-family self-preference bias.
- **C=0 sampling math**: 30 random clean units ⇒ <10% miss-rate at 95% confidence;
  60 ⇒ <5%. Flagged regions are always audited on top.
- **Cross-engine tripwire**: RapidOCR (Apache-2.0, pure pip, CPU/ONNX) disagreement
  flags tiles for mandatory audit — it is never the arbiter (it is the weaker
  extractor; the video frame is).
- **Bounded repair**: unbounded self-correction measurably degrades output; the loop
  requires concrete external evidence (validator output, frame diffs), strict
  improvement, and stops at 3 iterations.
- **Learning loop**: every failure updates `learning/LESSONS.md` + the affected
  rule/threshold in the same session (Rule 7) — a defect class seen once must be
  detectable thereafter.

Status: Stage A implemented and smoke-tested (`tools/validate_extraction.py` —
negative path FAILs correctly on a bare folder; positive path CLEAN/WARN on a
synthetic fixture). Stage B agent definition live. Workflow wired in
`system/workflows/INGEST_VIDEO.md`.

## 11. Pluggable parser backends (Phase 4)

`ParserBackend` protocol in `src/`: input = a segment's tiles + manifest entry; output =
Markdown + confidence. The default backend is `ClaudeInSession` — a no-op at pipeline
level (reconstruction happens in the INGEST_VIDEO workflow). MinerU / dots.ocr / Gemini
adapters become drop-ins later without touching the pipeline, the manifest schema, or
DO_TASK. See RESEARCH.md §3 for the candidate matrix.
