# RESEARCH — Video-Ingest Subsystem

Findings from two deep-research sweeps (2026-07-05) covering GitHub, HuggingFace,
arXiv, and vendor documentation. All claims carry citations; star counts and scores
are as fetched on that date.

## 0. Assumptions challenged (what changed from the original brief)

| Original assumption | Verdict | Replacement |
|---|---|---|
| "Give the video to a model; it reconstructs and solves" | **Rejected.** Video-native LLM ingestion is too lossy for small on-screen text: Gemini tokenizes video frames at 70 tok/frame (default) to 280 tok/frame (`media_resolution: high`), vs 560–2,240 tokens for the same content sent as an image. Google's own docs say `high` is needed for "dense text or small details" [5][6]. OpenAI and Anthropic APIs accept no video at all — frames only [7][8]. | Local preprocessing → stitched high-resolution page images → vision model reads images. |
| "Reconstruct everything into an editable document, then solve from it" | **Amended.** A pure two-stage design propagates transcription errors into verdicts. | Reconstruction = searchable index; stitched images = ground truth. Decisive values verified against images (matches the existing DO_TASK character-by-character protocol). |
| "This is a Document Understanding problem, not OCR" | **Partially right.** Document parsing IS commoditized (see §3) — neither the OCR nor the understanding layer is the novel work. The genuinely unsolved piece is upstream: **screen-recording → full-page image reconstruction (scroll stitching)**, which no mature project does (§1). | Build the stitcher (small, well-understood CV); keep parsing pluggable. |
| "There must be an existing project to reuse for video→document" | **Rejected.** Best prior art is edend10/stitch-it: 8 stars, 16 commits, no license, abandoned [1]. Windrecorder (3.9k★) indexes screen text for search but does not reconstruct documents [9]. | Reuse the mature *components* (PySceneDetect, imagehash, OpenCV) and own ~200–400 lines of glue + stitching logic. |

## 1. Video preprocessing & scroll stitching

**Mature, reusable components:**

- **PySceneDetect** (v0.7, actively maintained) — `ContentDetector`/`AdaptiveDetector`
  for hard tab/document switches; `HashDetector` (pHash-based) suits screen recordings
  with long static stretches [3]. A 2025 arXiv paper documents exactly this recipe:
  scene segmentation + pHash near-duplicate removal + keyframe scoring; notes SSIM is
  accurate but slow for long video (fine for a 90 s clip) [4].
- **imagehash** — perceptual hashing for dedup.
- **OpenCV** — the stitching algorithm is documented practice (Deepin's long-screenshot
  engineering post): grayscale both frames, take a strip of frame B as template,
  `cv2.matchTemplate` against frame A, threshold on normalized correlation, composite
  at the matched offset; `cv2.phaseCorrelate` gives sub-pixel translation as a
  cross-check [14][15].

**The gap — no packaged scroll-stitch-from-video project exists:**

- **edend10/stitch-it** — most on-point: `vid_stitch.py` turns a scrolling screen
  recording into one long screenshot. 8 stars, 16 commits, no license listed,
  effectively abandoned [1]. Useful as a proof the approach works; not reusable code.
- **jaflo/screenStitch**, **maxim-zhao/screenshot-autostitcher**,
  **spillerrec/Overmix** — screenshot-input (not video) stitchers; small/niche.
  Overmix has best-in-class alignment code but targets anime frames [2].
- Live-capture tools that stitch while *controlling* the scroll (not from an arbitrary
  mp4): ScrollSnap (macOS), macshot (macOS, Apple Vision stitch API), ScreenCapture
  (Windows/C++), scrollscreenshot (Android) [2][10]. Microsoft PowerToys still lists
  scrolling screenshot as an open feature request [10].
- Video-OCR tools (VideOCR, captiocr, Tesseract note-takers) extract text streams; none
  preserve document layout/fidelity [9].

**Failure modes we own** (they are the design's failure-mode table): sticky
headers/navbars, smooth-scroll motion blur, momentum scrolling, mixed scroll
directions, PDF page-snap viewers, zooming, multi-tab interleaving (handled by
segmentation first), cursor/highlight occlusion.

## 2. Can a frontier LLM just watch the video? (No — measured)

| Model | Video input | Key numbers | Verdict for small text |
|---|---|---|---|
| Gemini 2.5/3 | Yes, native | ~1 fps default sampling; Gemini 3: 70 tok/frame default, 280 at `high`; images get 560–2,240 tok [5][6] | Lossy at defaults; even `high` gives a frame a quarter of a high-res image's budget. Extracting stitched frames and sending them as images gives strictly more visual tokens per unit of content. |
| GPT-4o/5 (OpenAI) | No native video; cookbook pattern = extract frames [8] | — | Frames-as-images only; quality equals your preprocessing. |
| Claude (Anthropic) | Images only; GIFs use first frame [7] | — | Frames-as-images only — which is exactly the chosen design. |
| Qwen2.5-VL / Qwen3-VL (open, Apache-2.0) | Yes — dynamic fps, native dynamic per-frame resolution; Qwen3-VL adds explicit GUI/screen understanding [12][13] | Strongest open option for self-hosted video QA | Needs GPU — excluded by the CPU-only constraint; noted for Phase 4. |

Corroborating academic result: COLING 2025, "Do Current Video LLMs Have Strong OCR
Abilities?" finds significant gaps in video-LLM OCR [20]. Video text-spotting
benchmarks (TextVidBench [17], VidText [18], DSText V2 [19]) target natural-scene
text, not screen recordings; GUI-agent work (OmniParser [16], ScreenAI/Pix2Struct)
parses single screenshots into UI elements, not documents. **Screen-recording →
document reconstruction sits in an academic gap between video text spotting and GUI
agents.**

## 3. Document parsing (the pluggable layer) — comparison matrix

Consolidated 2025–2026 picture: compact specialist VLMs (0.9B–9B) that emit
Markdown/HTML/LaTeX directly now beat both classical pipelines and giant general VLMs
on document benchmarks [2b].

| System | Type/size | License | Hardware | OmniDocBench / olmOCR-Bench | Notes |
|---|---|---|---|---|---|
| **MinerU** (OpenDataLab) [5b] | pipeline + 1.2B VLM | Apache-derived w/ conditions | pipeline: CPU; VLM: ~8GB VRAM | **95.75** (formula CDM 97.45, table TEDS 93.42) / 75.2 | 73.5k★; accepts images & web pages; best open math+tables |
| **Marker** (Datalab) [6b] | pipeline + optional LLM | GPL code; revenue-capped weights | ~3.5GB VRAM | — / 76.1 | 37.2k★; fast; license flag for commercial use |
| **Docling** (IBM) [7b] | pipeline + 258M VLM | **MIT** | **CPU laptop-class** | edit-dist 0.589 vs MinerU 0.150 / — | 62.7k★; best license + easiest deploy; weakest math |
| **olmOCR-2** (AllenAI) [4b][8b] | 7B VLM | **Apache 2.0** | ≥12GB VRAM | — / 82.3 | English-only; renders pages at 1288 px longest side |
| **dots.ocr** (rednote) [3b] | 3B VLM | **MIT** | small GPU | — / 79.1 (dots.mocr 83.9) | tables 90.7%, multi-column 85.3%; JSON + bboxes |
| **DeepSeek-OCR** [10b] | 3B VLM | MIT-family | very efficient GPU | — / 75.7 | throughput champion, accuracy mid |
| **PaddleOCR-VL** [2b] | 0.9B VLM | open | modest GPU | 94.93 / ~80 | 109 languages |
| **Chandra** (Datalab) [2b] | 9B VLM | OpenRAIL (not fully open) | big GPU | — / **83.1** (open-weights #1) | |
| **GOT-OCR 2.0 / Nougat** | 580M / 350M | open / verify | 8GB / small | superseded | legacy tier |
| **Gemini 2.5/3 Flash (API)** [11b][12b][13b] | hosted | — | none | Gemini 3 Pro formula CDM 95.99 | ~$0.0002–0.001/page; excluded by the no-external-API decision, noted for Phase 4 |

Benchmark caveat: OmniDocBench (clean typeset pages — closest to our screenshots) and
olmOCR-Bench (degraded scans) rank systems differently; MinerU tops one and sits in the
bottom third of the other. Several top scores are vendor self-reported.

**Resolution sensitivity — good news for screen captures:** the "300 dpi" rule is a
classical-OCR (Tesseract-era) guideline. Modern doc VLMs downscale internally — olmOCR
processes pages at 1288 px longest dimension [8b] — so a 1440p capture is at/above what
these models see natively. Practical implication: record ≥1440p and keep body text
≥ ~14–20 px on screen; then screenshots parse like rendered PDF pages. Classical-OCR
pipelines (Docling default, MinerU pipeline backend) are the ones that degrade at
screen resolution.

**Math fallback if ever needed:** UniMERNet > Mathpix (commercial) > pix2tex > Texify
for formula-image→LaTeX [14b][15b]. MinerU already embeds UniMERNet-lineage formula
recognition, so a separate math stage only matters if a weak base parser is chosen.

**Web-page screenshots specifically:** no dedicated open "webpage screenshot →
Markdown" leader exists. Pix2Struct (screenshot→HTML pretraining) is 2022-era and needs
per-task fine-tuning [16b]; general doc VLMs and Claude/Gemini handle web screenshots
directly. If a live URL is ever available, DOM extraction beats any vision route.

## 4. Why Claude-in-session parsing was chosen for the MVP

1. **Confidentiality:** annotation task content already flows through Claude Code;
   adding Gemini/local models widens the disclosure surface for no MVP gain.
2. **Hardware:** the target machine is CPU-only; every strong open parser wants a GPU
   (Docling runs on CPU but is the weakest at math — the content's hardest element).
3. **Quality:** frontier-model vision on clean 1440p screen captures is competitive
   with specialist parsers on this content class (OmniDocBench-like, not degraded
   scans), and the index-vs-ground-truth principle means parsing errors cannot decide
   verdicts anyway.
4. **Reversibility:** the `ParserBackend` protocol (ARCHITECTURE §9) makes MinerU /
   dots.ocr / Gemini drop-ins if in-session fidelity proves insufficient in Phase 1
   testing.

## 5. Fidelity deep-dive I — pixel side (second sweep, 2026-07-05)

A dedicated critique sweep of the pipeline design. Verdicts on our original choices:

**Confirmed right:** template matching over ORB/SIFT for screen content (production
long-screenshot tools converged on exactly this [11]); phaseCorrelate cross-check
(Guizar-Sicairos upsampled-DFT is a stronger variant if needed [12c]); sticky-header
crop-and-restore; raw-keyframe fallback.

**Corrected (design updated accordingly):**
- **Recording settings are the #1 legibility lever, not post-processing.** H.264's
  deblocking filter smooths exactly the sharp edges text is made of [13c][14c]; 4:2:0
  chroma subsampling makes small colored text "partly unreadable" [15c]. CRF ≤16 +
  I444 (or lossless qp=0) at native resolution beats every enhancement idea combined
  [16c][17c]. → RECORDING_SOP hard requirement 0.
- **Multi-frame super-resolution is a dead end here.** Burst/handheld MFSR depends on
  sensor aliasing + hand-tremor sub-pixel offsets + RAW noise — none exist in rendered
  screen content [1c][2c]; static dwell frames are H.264 skip-block copies (bit-
  identical, nothing to fuse) [3c]. **Generative SR (Real-ESRGAN/BasicVSR++/diffusion)
  actively hallucinates text** ("gibberish that looks like text" [4c]; confirmed by
  TextSR [5c]) — banned from the pipeline.
- **Fixed 4 fps sampling → displacement-budget selection.** Fixed rate fails both
  ways: insufficient stitch overlap at fast scroll, waste at dwell; sparse sampling
  provably loses transient events [6c]. Full decode (~2,700 frames) + phase-corr dy on
  downsampled grayscale + one frame per ~35–40% viewport of scroll [7c][8c].
- **PySceneDetect ContentDetector → tab-bar signal primary.** Sustained scrolling is
  ContentDetector's documented camera-motion failure case [9c][10c]; AdaptiveDetector
  acceptable as secondary.
- **Variance-of-Laplacian sharpest-frame → last-frame-of-dwell.** Codec ringing
  inflates Laplacian variance (VoL can prefer the most artifacted frame); encoders
  progressively refine static content, so the dwell's last frame is cleanest [3c].
- **Compositing details:** integer offsets only (sub-pixel warping blurs 1-px
  strokes); hard cuts, no blending; cut on minimum-ink whitespace rows; guard
  low-variance strips (TM_CCOEFF_NORMED destabilizes on whitespace) and mask dynamic
  regions (caret blink, animations) [11].
- **Don't discard salience:** dwell time = importance signal; cursor is a gaze proxy
  (gaze leads cursor ~700 ms [21c][22c]); transient overlays (tooltips/popovers) are
  destroyed by stitching and must be emitted as anchored aux keyframes. Prior art for
  extraction at scale: VideoAgentTrek [8c].
- **Text-size floor for VLM OCR:** accuracy matches conventional OCR at ~42 px/char
  and cliffs below ~20 px/char [19c][20c] → never downscale tiles; Lanczos-upscale
  small text.

## 6. Fidelity deep-dive II — Claude input side (second sweep, 2026-07-05)

**The big catch — our tile geometry was wrong.** Verified numbers (July 2026):
- Claude Code's **Read tool clamps images to 2000×2000 px** before the API sees them
  [3d][4d]. Our planned 2560-wide tiles would arrive at 2000×1250 — a silent 22%
  linear resolution loss on every tile.
- API high-resolution tier (Fable 5 / Opus 4.8 / Sonnet 5): max long edge 2576 px,
  **max 4,784 visual tokens** per image; cost = `⌈w/28⌉ × ⌈h/28⌉` tokens (28-px
  patches) [1d][2d]. For portrait documents the token cap binds before the edge cap.
- Anthropic's own guidance: pre-resize client-side so the image you hold is the image
  Claude sees; image before text; label multiple images; hallucination risk rises for
  small/low-quality text [1d][2d].
- → Tile rule (ARCHITECTURE §2.8): crop to content-column width, ≤2000 px both sides,
  ≤4,784 tokens, whitespace-row cuts, 2–4-line overlap.

**Resolution vs accuracy:** ~150-DPI-equivalent suffices for strong models; going
higher buys little [14d]; the cliff is at ~7–8 px char height [9d]; olmOCR itself
runs at 1024 px longest edge [6d]. High-res tier matters for superscripts, footnotes,
dense tables — exactly our content.

**Anti-hallucination (published, adopted into the workflow):**
- **Document anchoring** — injecting (even noisy) extracted text alongside the image
  is olmOCR's single biggest hallucination reducer [6d][7d][8d] → optional Tesseract
  anchor pass, Phase 3.
- **Decorrelated verification** — same-model same-view re-reads make correlated
  errors; majority-vote over identical samples can underperform one good read [15d].
  Risk-controlled OCR gets CER 110.5%→8.4% by probing geometrically perturbed views
  and **abstaining on disagreement** [10d]; multi-VLM consensus (+42.1% F1) is the
  strongest published signal [11d]. → Spot-checks are zoomed crops; disagreement ⇒
  `[UNREADABLE]`, never a coin flip.
- **Failure taxonomy** to guard in prompts: plausible continuation past visible text,
  digit/ISBN substitution, repetition loops, truncation-completion at tile edges
  [10d][12d]. → `[CONTINUES]` marker, abstention-preferred instruction, low
  temperature, continue-after-text tile chaining.
- Budget: ~3.2–4.8k visual tokens per max tile; **15–25 tiles per subagent** leaves
  room for output tokens [1d].

## 7. QA-gate methodology (third sweep, 2026-07-05)

How to evaluate/validate extraction when the source video is the only ground truth:

- **Reference-free text-quality proxies are established practice**: lexicon hit-rate
  (unsupervised OCR profiling since 2013, used at national-library scale) [2e][5e][6e];
  gibberish/entropy detectors hit 97.5% good-vs-bad OCR classification while GPT-2
  perplexity was "too slow and unreliable" [1e]. Proxies rank quality; they don't
  certify fidelity — plausible hallucinations pass them. Caveat: they misfire on
  table-heavy content; relax thresholds there [1e].
- **Render-and-compare is current practice** (Visual-ERM renders markup back to an
  image and judges discrepancies; explicitly prevents reward-hacking where proxy
  metrics improve while fidelity degrades) [7e]. Pixel/SSIM comparison of a Markdown
  re-render vs a frame fails on font/wrap differences — the workable forms are
  structure comparison or a vision judge reading both; SSIM is reserved for stitch
  seams where pixels *should* match [7e][9e].
- **Acceptance sampling gives the audit math**: Rule of Three / C=0 plans — n random
  units with zero defects ⇒ 95% confidence true miss-rate < 3/n (30 units ⇒ <10%,
  60 ⇒ <5%) [11e][12e]. Stratify by time/scroll-position (video frames are
  correlated) and oversample fast-scroll stretches — the canonical miss location [22e].
- **Self-preference bias is measured and survives anonymization** (mechanism is
  familiarity/low perplexity of own text, not self-recognition) [13e][14e]. Mitigation
  with evidence: checklist/structured evaluation (−31.5% bias), reference-guided
  verdicts, evidence-required scoring, temperature 0 [14e][15e][23e]. Strongest
  structural fix (our adoption): make the judge do **perception + mechanical diff**
  (blind re-transcription), so the verdict comes from the diff, not an opinion.
- **Naive self-correction loops degrade output** (ICLR 2024: LLMs cannot reliably
  self-correct without external feedback; refined output not always better) [16e][18e].
  Working pattern: external-evidence-driven repair, targeted regions only, iteration
  cap (2–3), monotone-improvement requirement, keep best-ever, escalate on
  oscillation [16e][17e][18e][25e].
- **Mechanical oracles from the video**: scroll-distance conservation (Σ phase-corr
  offsets ≈ composite height − viewport) [20e][21e]; frame accounting; per-seam SSIM;
  CV text-line count vs transcription line count [4e]; cross-engine OCR agreement as
  a tripwire (the classical engine is weaker — flags disagreement, never arbitrates)
  [2e][5e]. Oracle *framing* is our inference; each ingredient is established.

Adopted design: `rules/EXTRACTION_QA_RULES.md` + `tools/validate_extraction.py`
(Stage A) + `.claude/agents/extraction-evaluator.md` (Stage B) + bounded repair loop.

## 8. Free tooling stack (third sweep, 2026-07-05)

Constraint set (binding, per user): Claude Code only, no external LLM APIs, no portal
login, open-source CPU-only Windows-friendly tools.

| Tool | Role | Verdict |
|---|---|---|
| **RapidOCR** (`pip install rapidocr`) | Primary decorrelated OCR verifier + future anchoring | ADOPT — Apache-2.0, pure pip, ONNX CPU, per-box confidence; PaddleOCR-lineage accuracy on rendered text [3f][4f]. Compare at line level (word-spacing quirk on Latin text) [1f] |
| **Tesseract 5** (UB Mannheim + pytesseract) | Second verifier; per-word 0–100 confidence; maximally decorrelated (LSTM lineage) [6f][7f][8f] | OPTIONAL — installer friction; add when double-tripwire wanted |
| **RapidLaTeXOCR** | Coarse equation check | OPTIONAL — MIT, ONNX CPU [16f]; all free math-OCR is pix2tex-descended and produces non-canonical LaTeX ⇒ token-set similarity only, never exact match; Claude crop+zoom re-reads remain primary for math |
| **ffmpeg/ffprobe via Bash** | Exact-frame extraction for audits (`-ss` after `-i`), recording preflight (pix_fmt/bitrate warnings), independent scene-detect cross-check (`select='gt(scene,t)'`, `freezedetect`) | ADOPT [25f][26f][30f] |
| **OpenCV morphology / DB / EAST** | Text-line counting as coverage oracle (no recognition cost) | ADOPT (morphology first — no model download; screen text is clean) [32f][33f] |
| **Windows.Media.Ocr / winocr** | — | SKIP as foundation: public API exposes NO confidence scores [10f]; `oneocr` has confidence but wraps a private engine — fragile [11f] |
| **EasyOCR** | — | SKIP — inactive maintenance, slow CPU [14f][15f] |
| **docTR/OnnxTR** | third neural opinion | SKIP unless ensemble diversity needed [12f] |
| **MCP servers** (ffmpeg-mcp, mcp-ocr, ImageSorcery…) | — | SKIP — thin wrappers over binaries Claude Code already drives via Bash with full control; they add config surface, not capability [20f]–[24f] |

Caveat: no published OCR benchmark targets *screen-rendered* text specifically;
rankings extrapolate from clean-printed-text comparisons [1f][2f] — worth a 20-image
self-benchmark on real frames during Phase 1.

## 9. Caveats / uncertainty

- Star counts, scores, and activity levels fetched 2026-07-05; the space moves fast
  (GLM-OCR, Infinity-Parser, dots.mocr all appeared within ~6 months). Re-check
  leaderboards before Phase 4 backend selection.
- Gemini token-per-frame figures differ across doc generations (258/66 for 2.5-era vs
  70/280 for Gemini 3) — verify against current docs if that path is ever taken.
- "No mature scroll-stitching project exists" is an inference from absence across many
  targeted searches — strong, but not provable.
- The claim that 1080p+ screenshots are sufficient for all VLM parsers extrapolates
  from olmOCR's confirmed 1288 px operating point; ROADMAP Phase 1 tests it empirically
  for Claude's Read tool (kill-risk experiment A1).
- Second-sweep caveats: the Claude Code 2000×2000 clamp is confirmed by official error
  docs [3d][4d], but whether images already ≤2000 px pass through fully untouched needs
  one empirical check (folded into A1). The ~7–8 px char-height cliff attribution [9d]
  should be verified against the primary paper before quoting. No published source
  prescribes tile-overlap percentages — the 2–4-line rule is inference. The
  MFSR-useless-for-screen-content conclusion combines burst-SR preconditions [1c][2c]
  with H.264 skip-block behavior [3c] — labeled inference, not a measured study.
  Whitespace-seam placement and VoL-vs-ringing are engineering inferences — cheap to
  A/B test in Phase 1.

## References

**Video / stitching / video-LLM sweep**
- [1] stitch-it — https://github.com/edend10/stitch-it
- [2] screenStitch — https://github.com/jaflo/screenStitch · Overmix — https://github.com/spillerrec/Overmix · screenshot-autostitcher — https://github.com/maxim-zhao/screenshot-autostitcher · ScrollSnap — https://github.com/Brkgng/ScrollSnap
- [3] PySceneDetect detectors — https://www.scenedetect.com/docs/latest/api/detectors.html
- [4] Scene Detection Policies and Keyframe Extraction Strategies for Large-Scale Video Analysis — https://arxiv.org/html/2506.00667v1
- [5] Gemini API video understanding — https://ai.google.dev/gemini-api/docs/video-understanding
- [6] Gemini API media resolution — https://ai.google.dev/gemini-api/docs/media-resolution
- [7] Claude vision docs (images only) — https://platform.claude.com/docs/en/build-with-claude/vision
- [8] OpenAI no native video — https://github.com/openai/openai-node/issues/1778 · frames cookbook — https://cookbook.openai.com/examples/gpt_with_vision_for_video_understanding
- [9] Windrecorder — https://github.com/yuka-friends/Windrecorder
- [10] macshot — https://github.com/sw33tLie/macshot · PowerToys request — https://github.com/microsoft/PowerToys/issues/33336
- [12] Qwen2.5-VL technical report — https://arxiv.org/pdf/2502.13923
- [13] Qwen3-VL — https://github.com/qwenlm/qwen3-vl · https://arxiv.org/pdf/2511.21631
- [14] Deepin long-screenshot principles — https://medium.com/@deepinlinux/technical-sharing-screen-capture-principles-of-long-screenshots-418e59d81d3c
- [15] OpenCV template matching — https://docs.opencv.org/4.13.0/d4/dc6/tutorial_py_template_matching.html
- [16] Microsoft OmniParser — https://github.com/microsoft/OmniParser
- [17] TextVidBench — https://arxiv.org/abs/2506.04983
- [18] VidText — https://arxiv.org/html/2505.22810v1
- [19] DSText V2 — https://arxiv.org/pdf/2312.01938
- [20] Do Current Video LLMs Have Strong OCR Abilities? (COLING 2025) — https://aclanthology.org/2025.coling-main.659.pdf

**Document parsing sweep**
- [1b] OmniDocBench — https://github.com/opendatalab/OmniDocBench
- [2b] Supercharge your OCR Pipelines with Open Models (HF) — https://huggingface.co/blog/ocr-open-models
- [3b] dots.ocr — https://github.com/rednote-hilab/dots.ocr · paper — https://arxiv.org/pdf/2512.02498
- [4b] olmOCR — https://github.com/allenai/olmocr
- [5b] MinerU — https://github.com/opendatalab/MinerU · MinerU2.5 paper — https://arxiv.org/pdf/2509.22186
- [6b] Marker — https://github.com/datalab-to/marker
- [7b] Docling — https://github.com/docling-project/docling · vs MinerU — https://www.codesota.com/ocr/docling-vs-mineru
- [8b] olmOCR-2-7B model card (1288 px) — https://huggingface.co/allenai/olmOCR-2-7B-1025
- [10b] DeepSeek-OCR — https://huggingface.co/deepseek-ai/DeepSeek-OCR
- [11b] Reducto: Mistral OCR vs Gemini Flash — https://reducto.ai/blog/lvm-ocr-accuracy-mistral-gemini
- [12b] OCR Arena comparisons — https://www.ocrarena.ai/compare/gemini-2-5-pro/mistral-ocr-v3
- [13b] Gemini Flash PDF cost analysis — https://gigazine.net/gsc_news/en/20250210-ingesting-pdf-gemini-2-0
- [14b] UniMERNet — https://arxiv.org/html/2404.15254v1
- [15b] Texify — https://github.com/VikParuchuri/texify
- [16b] Pix2Struct — https://arxiv.org/abs/2210.03347

**Fidelity deep-dive I — pixel side (§5)**
- [1c] Handheld Multi-Frame Super-Resolution (Google Research) — https://sites.google.com/view/handheld-super-res/
- [2c] Implementing Handheld Burst Super-resolution (IPOL 2023) — https://www.ipol.im/pub/art/2023/460/article_lr.pdf
- [3c] H.264 skip-block behavior in static content (Amped FIVE macroblocks) — https://blog.ampedsoftware.com/2023/07/19/how-to-use-the-macroblocks-filter-in-amped-five
- [4c] Real-ESRGAN/BasicVSR++ engineering playbook (text hallucination) — https://www.forasoft.com/learn/ai-for-video-engineering/articles-ai/real-esrgan-basicvsr-ott-archive-upscaling
- [5c] TextSR: Diffusion SR with Multilingual OCR Guidance — https://arxiv.org/abs/2505.23119
- [6c] Benchmarking GUI Agents in High-Dynamic Environments — https://arxiv.org/html/2604.25380v2
- [7c] Adaptive Keyframe Sampling (CVPR 2025) — https://openaccess.thecvf.com/content/CVPR2025/papers/Tang_Adaptive_Keyframe_Sampling_for_Long_Video_Understanding_CVPR_2025_paper.pdf
- [8c] VideoAgentTrek: Computer Use Pretraining from Unlabeled Videos — https://arxiv.org/html/2510.19488
- [9c] PySceneDetect detectors — https://www.scenedetect.com/docs/latest/api/detectors.html
- [10c] ContentDetector camera-motion false positives (issue #153) — https://github.com/Breakthrough/PySceneDetect/issues/153
- [11] Deepin long-screenshot principles (also cited in §1) — https://medium.com/@deepinlinux/technical-sharing-screen-capture-principles-of-long-screenshots-418e59d81d3c
- [12c] phase_cross_correlation (Guizar-Sicairos upsampled DFT) — https://scikit-image.org/docs/stable/auto_examples/registration/plot_register_translation.html
- [13c] HEVC Screen Content Coding extension overview (MERL) — https://www.merl.com/publications/docs/TR2015-126.pdf
- [14c] Intra Block Copy in HEVC-SCC — https://www.semanticscholar.org/paper/5b8ef0e83b1e839a3ef62ab9821334247878444d
- [15c] Chroma subsampling 4:4:4 vs 4:2:0 (RTINGS) — https://www.rtings.com/tv/learn/chroma-subsampling
- [16c] OBS Advanced Recording Settings Guide — https://obsproject.com/kb/advanced-recording-settings-guide
- [17c] OBS lossless recording — https://obsproject.com/forum/threads/how-to-record-lossless-quality.71369/
- [19c] Context-Independent OCR with Multimodal LLMs: resolution effects — https://arxiv.org/html/2503.23667v1
- [20c] Minimum pixel resolution for OCR (Cognex) — https://support.cognex.com/en/help-articles/in-sight-what-is-the-minimum-pixel-resolution-recommended-to-ocr-human-readable-text
- [21c] Eye/mouse movement correlation on web browsing — https://dl.acm.org/doi/10.1145/634067.634234
- [22c] Mouse-click vs eye-movement attention tracking — https://pmc.ncbi.nlm.nih.gov/articles/PMC7908465/

**Fidelity deep-dive II — Claude input side (§6)**
- [1d] Vision — Claude Platform Docs (tiers, limits, guidance) — https://platform.claude.com/docs/en/build-with-claude/vision
- [2d] Coordinates & bounding boxes / resize rules + resized_size() — https://platform.claude.com/docs/en/build-with-claude/vision-coordinates
- [3d] Claude Code error reference (2000×2000 image clamp) — https://code.claude.com/docs/en/errors
- [4d] Claude Code issue #53170 (image dimension limits) — https://github.com/anthropics/claude-code/issues/53170
- [6d] olmOCR paper (document anchoring, 1024 px operating point) — https://arxiv.org/abs/2502.18443
- [7d] olmOCR explained — https://ritvik19.medium.com/papers-explained-326-olmocr-bc9158752901
- [8d] olmOCR blog (Ai2) — https://allenai.org/blog/olmocr
- [9d] H2OVL-Mississippi technical report (char-height cliff; attribution to verify) — https://arxiv.org/pdf/2410.13611
- [10d] Risk-Controlled Generative OCR (perturbed views + abstention) — https://arxiv.org/html/2603.19790v1
- [11d] Consensus Entropy: multi-VLM agreement for self-verifying OCR — https://arxiv.org/abs/2504.11101
- [12d] VLM OCR production failure modes (LlamaIndex) — https://www.llamaindex.ai/blog/engineering-insights-failure-modes-that-break-vlm-powered-ocr-in-production
- [14d] Local VLM OCR benchmark (DPI sufficiency) — https://nullmirror.com/en/blog/2026-05-24-local-vision-language-ocr-benchmark/
- [15d] Vote-accuracy curve of repeated LLM inference (correlated errors) — https://arxiv.org/html/2605.03379

**QA-gate methodology (§7)**
- [1e] OCR Accuracy Metrics Without Ground Truth Data — https://generic-account.github.io/OCR-Accuracy-Without-Ground-Truth-Data.html
- [2e] Evaluation of HTR Models without Ground Truth (LREC 2022) — https://aclanthology.org/2022.lrec-1.467.pdf
- [4e] Layout-Aware OCR: Unsupervised Evaluation — https://arxiv.org/html/2509.13236v1
- [5e] Survey of OCR evaluation tools and metrics — https://dl.acm.org/doi/fullHtml/10.1145/3476887.3476888
- [6e] Lexical quality estimation of OCRed Finnish newspapers — https://arxiv.org/pdf/1611.05239
- [7e] Visual-ERM: Reward Modeling for Visual Equivalence — https://arxiv.org/html/2603.13224v1
- [9e] go-regress: visual regression via SSIM — https://github.com/Pondigo/go-regress
- [11e] Rule of three (statistics) — https://en.wikipedia.org/wiki/Rule_of_three_(statistics)
- [12e] C=0 sampling plan table — https://qscompliance.com/c0-sampling-plan-table/
- [13e] Self-Preference Bias in LLM-as-a-Judge — https://arxiv.org/html/2410.21819v1
- [14e] Quantifying and Mitigating Self-Preference Bias — https://arxiv.org/html/2604.22891v1
- [15e] LLMs-as-Judges: A Comprehensive Survey — https://arxiv.org/pdf/2412.05579
- [16e] LLMs Cannot Self-Correct Reasoning Yet (ICLR 2024) — https://arxiv.org/abs/2310.01798
- [17e] Self-Refine — https://selfrefine.info/
- [18e] CYCLE: Learning to Self-Refine Code Generation — https://dl.acm.org/doi/pdf/10.1145/3649825
- [20e] Phase-correlation overlap for stitching — https://answers.opencv.org/question/189755/
- [21e] Principles of Long Screenshots — https://medium.com/@deepinlinux/technical-sharing-screen-capture-principles-of-long-screenshots-418e59d81d3c
- [22e] OCR text redaction in screen recordings (fast-scroll misses) — https://vidizmo.ai/blog/ocr-based-text-redaction-screen-recordings
- [23e] VLM-as-a-Judge evaluation protocol — https://www.emergentmind.com/topics/vlm-as-a-judge-evaluation-protocol
- [25e] CoRefine: Confidence-Guided Self-Refinement — https://arxiv.org/pdf/2602.08948

**Free tooling stack (§8)**
- [1f] Open-source OCR developer comparison — https://invoicedataextraction.com/blog/open-source-ocr-invoice-extraction
- [2f] Best Python OCR library 2026 — https://www.codesota.com/ocr/best-for-python
- [3f] RapidAI/RapidOCR — https://github.com/RapidAI/RapidOCR
- [4f] rapidocr on PyPI — https://pypi.org/project/rapidocr/
- [6f] Tesseract downloads (tessdoc) — https://tesseract-ocr.github.io/tessdoc/Downloads.html
- [7f] UB-Mannheim/tesseract — https://github.com/UB-Mannheim/tesseract/wiki
- [8f] Tesseract TSV word confidence — https://medium.com/geekculture/tesseract-ocr-understanding-the-contents-of-documents-beyond-their-text-a98704b7c655
- [10f] OcrWord API (no confidence) — https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrword
- [11f] oneocr — https://pypi.org/project/oneocr/
- [12f] OnnxTR — https://github.com/felixdittrich92/OnnxTR
- [14f] easyocr package health — https://security.snyk.io/package/pip/easyocr
- [15f] EasyOCR2 announcement — https://github.com/JaidedAI/EasyOCR/issues/1447
- [16f] RapidLaTeXOCR — https://github.com/RapidAI/RapidLaTeXOCR
- [20f] ffmpeg-mcp — https://github.com/video-creator/ffmpeg-mcp
- [21f] mcp-video — https://github.com/KyaniteLabs/mcp-video
- [22f] video-audio-mcp — https://github.com/misbahsy/video-audio-mcp
- [23f] mcp-ocr — https://github.com/rjn32s/mcp-ocr
- [24f] ImageSorcery MCP — https://playbooks.com/mcp/sunriseapps-imagesorcery
- [25f] ffmpeg frame extraction (-ss placement) — https://www.ffmpeg-micro.com/blog/extract-frames-from-video-ffmpeg
- [26f] ffprobe documentation — https://ffmpeg.org/ffprobe.html
- [30f] ffmpeg filters (scene/freezedetect/blackdetect) — https://ffmpeg.org/ffmpeg-filters.html
- [32f] OpenCV TextDetectionModel (DB/EAST) — https://docs.opencv.org/4.x/d4/d43/tutorial_dnn_text_spotting.html
- [33f] OpenCV EAST text detection — https://pyimagesearch.com/2018/08/20/opencv-text-detection-east-text-detector/
