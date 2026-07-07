# LESSONS — video-ingest pipeline learning loop (append-only)

Contract (EXTRACTION_QA_RULES §7): every QA failure, escalation, or defect that
escapes the gate gets an entry here, and the affected rule/threshold/check is updated
in the same session. Entries are never deleted; superseded ones are marked.

Format:
```
## YYYY-MM-DD — <short title>
- What happened:
- Root cause:
- Detection gap: (why didn't Stage A / Stage B catch it, or how did it catch it late)
- Change made: (file + rule/threshold/check updated)
```

---

## 2026-07-05 — Seed: design-time lessons adopted before first run

- What happened: three research sweeps (RESEARCH.md §5–8) corrected the initial
  design before any code ran.
- Lessons folded in as rules, recorded here so they survive doc rewrites:
  1. Tile geometry must respect Claude Code's 2000×2000 Read clamp — never rely on
     silent downscaling (ARCHITECTURE §2.8).
  2. Recording settings (CRF ≤16, I444) outweigh all post-processing
     (RECORDING_SOP req 0).
  3. Generative super-resolution is banned — it can rewrite evidence
     (ARCHITECTURE §2.4).
  4. Self-judging is biased lenient — evaluator uses blind re-transcription +
     mechanical diff, never opinions (EXTRACTION_QA_RULES §2).
  5. Unbounded repair loops degrade output — max 3 targeted iterations, monotone
     improvement, keep best-ever (EXTRACTION_QA_RULES §5).
- Change made: rules created (EXTRACTION_QA_RULES.md), evaluator agent created
  (.claude/agents/extraction-evaluator.md), validator created
  (video_pipeline/tools/validate_extraction.py).

## 2026-07-05 — First seeded-defect drill: A7 cross-engine tripwire verified live

- What happened: on a synthetic fixture (tile with rendered text incl. an ISBN line),
  the reconstruction was deliberately left missing the ISBN + heading lines. Stage A
  check A7 (RapidOCR vs reconstruction, 70% token-overlap threshold) flagged the tile
  at 68% and put it on the mandatory Stage-B audit list. After completing the
  reconstruction, A7 cleared to CLEAN. Negative path also verified: bare folder ⇒
  FAIL on missing video + manifest.
- Root cause: n/a (drill, not a defect).
- Detection gap: none for this class; note the 70% threshold caught a ~2-line-in-20
  omission — sensitivity on real dense pages still needs calibration during Phase 1.
- Change made: none yet; threshold (0.70) confirmed as a reasonable starting point,
  marked for tuning against real recordings (ROADMAP Phase 3 threshold-tuning item).

## 2026-07-05 — First real task (task2, qa_022): A7 fires systematically on form-chrome panels

- What happened: first end-to-end ingest of a real recording (task2, 67.7s, 2538x1340,
  yuv420p). MVP ran in keyframes-only mode (no stitcher yet): 48 keyframes, 2 segments,
  81 panel tiles. Stage A pass 2: A5/A1/A2/A4/A6 CLEAN; A7 flagged 20 tiles — and ALL 20
  were `_right.png` (the question/answer + annotation-form panel). Zero evidence-content
  (`_left.png`) tiles were flagged.
- Root cause: the right panel is mostly non-evidence chrome — the empty annotation form,
  grey placeholder text ("Paste the relevant evidence text here", "Example: [Page 37]…"),
  and the platform "Special Cases"/"PDF Reference" instruction block. The reconstruction
  (question_panel.md) intentionally CONDENSES this chrome and transcribes verbatim only
  the decisive values (question text, Answer=337, Format/Verify line). RapidOCR reads all
  the chrome verbatim, so token overlap vs the condensed reconstruction sits at 47–69%,
  below the 0.70 tripwire — a systematic false-positive class, not content loss.
- Detection gap: A7 cannot distinguish "intentionally-condensed non-evidence chrome" from
  "lost content." By design it is a tripwire, not an arbiter (RESEARCH §8) — Stage B
  (evaluator vs base video) is the arbiter and resolves the class. Working as intended,
  but noisy: 20 mandatory audit items that are all the same benign pattern.
- Change made (this session): none to thresholds yet — deferring to Stage B confirmation.
  Candidate fix for Phase 3 (logged, not yet applied): tag tiles by panel role in the
  manifest (evidence vs form-chrome) and either (a) exclude known form-chrome panels from
  A7, or (b) compare chrome tiles only against a dedicated `chrome`/form reconstruction so
  the comparison is like-for-like. Do NOT simply lower the 0.70 threshold — that would
  blind A7 on real evidence tiles. Revisit once the stitcher + segment.py panel-role
  tagging exist (ROADMAP Phase 2/3).
- Also observed: doc-reconstructor subagents hit spurious `Output blocked by content
  filtering policy` API errors on 2 of 6 segments (doc1_p6 Editor's Preface, the PDF/revisit
  sweep). Benign academic fracture-mechanics text — a false trip of the output filter, not
  a content issue. Mitigation used: orchestrator reconstructed those segments directly from
  probe frames + task file. Phase 3: consider smaller per-dispatch tile batches and a retry
  path in INGEST_VIDEO for filter-blocked segments.
- End-to-end result: the full gate chain ran on task2 with no manual screenshots —
  Stage A WARN (A7 chrome-only) → reconstruction 6 docs → Stage A CLEAN(A5)/WARN(A7) →
  extraction-evaluator PASS (40 units, 0 defects) → completeness PASS (7 tabs) →
  DO_TASK all 5 agents → final-evaluator SHIP. Verdict: Correct (337 = Crevasses 373 −
  Earthquakes 36), independent-solver reached 337 blind. FIRST full video→submission run.
- MVP scope confirmed sufficient for a Contents-page comparison task: keyframes-only mode
  (no stitcher) was adequate because the decisive values are single-line Contents entries,
  each fully legible in one 1350px panel tile. The stitcher becomes load-bearing only when
  a decisive value spans a scroll boundary — not the case here. A1 legibility kill-risk is
  effectively passed for this task class: Claude Read transcribed 373/36 and 9 chapter
  page-numbers character-exact from panel tiles at 2538-wide/CRF-unknown yuv420p.

## 2026-07-05 — Speed pass after task2: cut wasted motion without touching a gate

Post-task self-audit of where wall-clock went, and the fixes shipped + validated:

1. **extraction-evaluator re-extracted ~30 audit frames via `ffmpeg -ss` seeks (338s,
   131k tokens) — the single biggest cost.** The pipeline had ALREADY saved those exact
   frames losslessly at `ingest/keyframes/f*.png`. Fix: the evaluator now decodes the
   saved keyframes directly for the bulk of the audit, guarded by a 3-frame fidelity
   spot-check (extract fresh, compare content) so "base video is source of truth" is
   preserved by acceptance-sampling the frame store rather than distrusting it wholesale.
   Batched fresh extractions into one `select=` call. Expected ~338s → ~30s. (Agent doc
   updated; principle, not yet re-timed on a live task.)

2. **Tab grouping detour: I OCR'd all 81 full tiles then grepped breadcrumbs, and did the
   split-x + grouping by hand.** Fixes: (a) `ingest.py` defaults split to mid-width (the
   Henna two-panel layout; auto-gradient detection was tried and was WRONG at 1377 vs the
   correct 1269 — removed as unreliable); (b) new `tools/label_tabs.py` OCRs only the
   evidence panel's breadcrumb box, pixel-diff-cached so a run of identical breadcrumbs
   costs one OCR call — 155s→104s, and it writes `tab_label` + `tab_groups.json` for
   auto-dispatch. Two bugs found and fixed during validation: the breadcrumb regex
   false-matched the form panel's instruction text ("Tabs are labeled Doc1 P5…") →
   REQUIRE `.pdf` in the crumb; and iterating all panels doubled the work → OCR the
   evidence panel only, decide the form panel by elimination (no OCR of its 35 tiles).
   REMAINING WEAKNESS (Phase 3): groups are approximate — single-tab pages (Doc1 P7/P8/P9)
   whose breadcrumb OCR misses get folded into a neighbor; the reconstructor verifies each
   breadcrumb so this is a sharding hint, not a correctness risk, but grouping precision
   should improve (sticky-header detection / OCR the tab-bar highlight instead of crumb).

3. **A7 flagged 20 benign form-chrome tiles (all `_right`).** Fix: `label_tabs.py` stamps
   authoritative `panel_role` (evidence vs form-chrome, from breadcrumb presence);
   `validate_extraction.py` A7 now skips `panel_role in {static, form-chrome}` and reports
   how many it excluded by design. The tripwire now fires only on evidence tiles.

4. **ingest tile dedup tightened** (TILE_CHANGE 1.0→3.0, ignores caret/subpixel scroll):
   81→71 tiles. A provisional variance-based panel_role is written by ingest and then
   overridden by label_tabs' OCR-grounded role.

5. **doc-reconstructor** now caps dispatches at ≤12 tiles and documents a
   narrow-slice re-dispatch path for the spurious content-filter blocks (2/6 hit them).

6. **Process rule added (user directive): INGEST_VIDEO Step 8 — LESSONS entry + session
   handoff after EVERY task, mandatory.** A task is not done until its learning is written.

Net: no gate removed, no quality traded. The wins are removing re-extraction, replacing a
manual full-tile OCR/grouping detour with a cached evidence-panel labeler, and silencing a
systematic false-positive class. Split-x auto-detect and tab-group precision remain open.

## 2026-07-05 — Second real task (task3, qa_035): speed pivot mid-run + label_tabs mis-grouping

- What happened: second end-to-end ingest (task3, string-theory cross-doc, counterfactual;
  1770 frames, 2538x1336, 56 keyframes, 93 tiles, split 1269, coverage 0 orphans). Mid-task
  Suraj directed: extraction is over-invested — it is *means*, DO_TASK is the *end*; get the
  whole extraction to ~2-3 min and prioritise the actual answering workflow. Delivered:
  Verdict **Correct** (N=1 massless spin-1 photon field A_μ(x)); independent-solver reached it
  blind; full 5-agent gate chain passed (reviewer-simulator REJECT→fix, humanizer, final-
  evaluator SHIP + HUMANIZATION PASS).
- Root cause of the slowness: (a) `label_tabs.py` OCR (~100 s) MIS-GROUPED — it folded three
  tabs (Doc2 P42-43, Doc2 P44-45, Doc3 P19) into one 22-tile "Doc2 P42" bucket (breadcrumb
  pixel-diff cache reused the label across tab switches) and labelled the PDF-reference tab as
  "Doc1 P38" (same `9781848162150.pdf … Page 38` breadcrumb string as the markdown tab). So the
  slow step produced a sharding I had to redo by hand anyway. (b) 6 reconstructor dispatches +
  many orchestrator frame-reads for a task whose decisive evidence I could read directly.
- Detection gap: none for correctness — coverage was confirmed by direct frame reads (all 5
  tabs + PDF present) and the reconstructor verifies each breadcrumb, so mis-grouping is a
  sharding hint, not a content risk. The gap is *efficiency*: label_tabs cost time and gave a
  wrong grouping.
- Changes made (this session):
  1. **INGEST_VIDEO.md — "Speed profile" (sanctioned fast path):** when the pasted task card
     already lists the tabs, skip label_tabs and shard by reading a few boundary-frame
     breadcrumbs; self-reconstruct short decisive tabs (≤2-3 frames) inline instead of
     dispatching; skip the slow A7-OCR/Stage-B re-runs when decisive values are frame-verified
     AND triangulated across ≥2 sources (logged as a deliberate deviation, never silent). Gate
     *intent* (coverage + decisive-value verification) unchanged; only redundant re-verification
     of already-verified content is trimmed. This task used the fast path and still passed every
     DO_TASK gate.
  2. **ingest.py — global page dedup:** a candidate tile is now compared to ALL previously
     emitted tiles of that panel (not just the immediate predecessor); a near-identical
     scroll-back revisit (`DUP_DIFF < 1.5` mean-abs-diff) is dropped and reported in
     INGEST_REPORT + manifest `coverage.dropped_duplicate_tiles`. Coverage invariant preserved
     (raw keyframes still represent every kept frame). VALIDATED on task3: 0 tiles dropped,
     coverage 56/56 — because task3's "revisits" are the PDF-reference tab (the original PDF
     *image* of Doc1 P38), which is genuinely different pixels from the markdown rendering, so
     the guard correctly did NOT drop them. Honest result: the change is a safe correctness/
     transparency guard, not a speed win on this particular recording — the real time was in
     label_tabs + over-reconstruction (addressed by change 1).
- Counterfactual handling: the altered element was Doc3's leading-Regge mass law
  `m ~ √(2(s−1))` / `(p²−2(s−1))H=(p²−m²)H=0` (extra factor 2 vs textbook `α'm²=s−1`). It does
  NOT change the s=1 result: 2(s−1) still vanishes at s=1 ⇒ m²=0, so the shared member is the
  standard N=1 photon. independent-solver flagged and correctly dismissed the trap.
- Gate-chain friction worth noting: reviewer-simulator and final-evaluator both caught
  **quote-integrity** defects on the dense LaTeX (a stitched non-contiguous Doc3 quote with an
  annotator connective inside the quotes field; a mid-sentence Doc1 quote; a note fact not
  backed by a cited quote). All were real and fixed. Lesson for future physics tasks: when a
  page interleaves prose and numbered display equations, quote each fragment as its own
  contiguous `[DocN Page Y] "..."` and keep ALL connective reasoning in the Note; make sure
  every Note claim maps to a cited quote (don't credit a doc for a fact you only cited from the
  other doc).
- Open (Phase 3): label_tabs grouping precision (detect the highlighted tab-bar button /
  sticky-header, don't rely on cached breadcrumb OCR); make label_tabs auto-skip when a tab
  list is supplied; extraction-evaluator keyframe-reuse still not re-timed on a live task
  (fast path skipped Stage-B this run by design).

## 2026-07-06 — Third real task (task4, qa_006): fast path proven on a set_difference MC task

- What happened: third end-to-end ingest (task4, cross-doc publication-data comparison,
  set_difference tag, multiple-choice; 1417 frames, 2530x1338, 38 keyframes, 58 tiles,
  split 1265, coverage 0 orphans). Ran the new INGEST_VIDEO fast path start-to-finish:
  skipped `label_tabs.py` entirely (task card listed the 6 tabs), mapped coverage by reading
  ~8 boundary keyframes, self-reconstructed only the 2 DECISIVE copyright pages (Doc1 P5,
  Doc2 P5) inline — no `doc-reconstructor` dispatches at all — then ran the full DO_TASK
  5-agent chain. Result: Verdict **Correct** (option **D** — both books list one ISBN, no
  extra label); independent-solver reached D blind; reviewer-simulator REJECT→fix, humanizer,
  final-evaluator SHIP + HUMANIZATION PASS.
- Why the fast path was safe here: the question is a set difference over publication-data
  labels (ISBN / e-book|eISBN / ISSN|series ISSN / DOI), which live ONLY on each book's
  copyright page. I read both copyright pages directly off the base frames (f00660_left Doc1
  P5, f00912/f00935_left Doc2 P5), plus every other front-matter page (covers, half-titles,
  blanks, contents) to confirm none carries a hidden ISSN/DOI. Decisive absence was verified
  against ground truth, and the evidence-hunter independently re-confirmed it frame-by-frame.
  Extraction took a few minutes instead of the full label_tabs+6-reconstructor path.
- The set_difference trap (and how it was defused): options A/B/C each assert Properties has an
  EXTRA identifier (e-book, DOI, ISSN) that Electron Scattering lacks. The trap is a second
  identifier line cut off below the ISBN, or a series ISSN on a half-title. Both were checked:
  the line after each ISBN is print/typeset info, not an identifier, and Doc2 P2 is a plain
  half-title, P3 blank. {ISBN}−{ISBN}=∅ ⇒ D. Lesson: for set_difference/publication-data MC,
  the decisive move is exhaustively enumerating PRESENCE and ABSENCE on the copyright page(s)
  and explicitly ruling out a cut-off second line — absence is the answer, so it must be proven,
  not assumed.
- Gate friction (recurring pattern across task3 + task4): reviewer-simulator again caught a
  **stitched-quote** integrity defect — two non-contiguous copyright lines ("This book is
  printed on acid-free paper." + "Printed in Singapore by Uto-Print") merged into one quoted
  string. Same class as task3's Doc3 stitch. STANDING RULE reinforced: never join
  non-adjacent page lines inside one `[DocN Page Y] "..."`; split into separate citations. This
  is now the single most common send-back cause on these tasks — pre-check every multi-clause
  quote for a paragraph/line break before drafting.
- Coverage/verdict result: full gate chain green, no manual screenshots, extraction fast.
  fast path validated on a second task class (publication-data set difference) after task3's
  physics-Regge class.
- Open (unchanged): label_tabs auto-skip when tabs supplied; grouping precision; extraction-
  evaluator keyframe-reuse still not live-timed (fast path skipped Stage-B by design again).

## 2026-07-06 — Fourth real task (task5, qa_002): temporal cross-doc; reviewer APPROVE first pass

- What happened: fourth end-to-end ingest (task5, temporal MC comparing two book volumes'
  copyright years vs a stated cadence; 1960 frames, 2516x1338, 80 keyframes, 111 tiles,
  split 1258, coverage 0 orphans). Fast path again: skipped label_tabs (card lists 6 tabs +
  PDF), mapped coverage from boundary frames, self-reconstructed 3 decisive pages inline
  (Doc1 P4 Vol6 copyright, Doc2 P8 Vol8 copyright, Doc2 P9 Preface) — no doc-reconstructor
  dispatches. Result: Verdict **Correct** (option **D** — 1995→1998, 1.5 yr/vol, slower than
  annual); independent-solver reached D blind with code; **reviewer-simulator APPROVED on the
  first pass** (no send-back); humanizer, final-evaluator SHIP + HUMANIZATION PASS.
- The temporal crux & trap: Doc1 P4 gives Vol 6 © 1995; Doc2 P8 gives Vol 8 © 1998; Doc2 P9
  Preface states "published volume number 6 in 1995 and number 7 in 1996" AND "The series will
  continue to be published with a frequency of one per year." Arithmetic (done with code, per
  prime directive): (1998−1995)/(8−6) = 3/2 = 1.5 yr/vol > 1.0 ⇒ slower than annual ⇒ D. The
  distractors are pure temporal traps: B swaps in 1997 for Vol 8, C swaps in 1996 (which is
  Vol 7's year, not Vol 6's) — the Preface's explicit "Vol 6 in 1995 / Vol 7 in 1996" is what
  disambiguates and kills C. Lesson: for temporal MC, the year→entity mapping is the trap;
  find the source sentence that binds each year to its specific entity, don't infer from the
  copyright page alone.
- First reviewer APPROVE with no send-back across the four tasks — attributable to pre-splitting
  every multi-line citation into separate `[DocN Page Y]` quotes BEFORE drafting (the standing
  rule from task3/task4). Applying that rule proactively eliminated the recurring stitched-quote
  send-back. This confirms the rule is worth doing up front, not waiting for the reviewer to
  catch it: it saves a full reviewer→fix→re-review cycle.
- Fast path now validated across three task classes: physics-Regge (task3), publication-data
  set-difference (task4), temporal volume-cadence (task5). Extraction stayed to a few minutes
  each; correctness earned entirely in the DO_TASK 5-agent chain.
- Open (unchanged): label_tabs auto-skip when tabs supplied; grouping precision; extraction-
  evaluator keyframe-reuse STILL not live-timed (fast path has now skipped Stage-B by design on
  three consecutive tasks — if a future task's decisive value is single-sourced or unreadable,
  Stage-B must run and this claim finally gets measured).

## 2026-07-06 — Fifth real task (task6, qa_048): comparison/5-doc; Pass-1 stride speed cut + first WRONG verdict

- What happened: fifth end-to-end ingest (task6, cross-doc "comparison" MC over FIVE PSB volumes'
  conference date lines; 1530 frames, 2542x1338, stride 3 → 509 sampled, 42 keyframes, 65 tiles,
  split 1271, coverage 0 orphans). Fast path again (card lists all 7 tabs). Result: Verdict
  **Wrong** — first Wrong verdict of the series; independent-solver reached option **D** blind
  with code; reviewer-simulator REJECT→note-fix→APPROVE; humanizer, final-evaluator SHIP +
  HUMANIZATION PASS.
- User speed directive (this task): "cut down not so important steps … we dont need so many pages
  to be extracted of each frame … faster way … more focus on the actual task." Delivered a real
  Pass-1 speedup in `ingest.py`:
  1. **Frame-stride sampling (ANALYSIS_STRIDE=3, `--stride` flag).** Pass 1 was decoding EVERY
     frame at full res + running phaseCorrelate on every consecutive pair — the pipeline's
     dominant cost. Screen recordings dwell ~1 s per page, so sampling every 3rd frame (10 fps @
     30 fps source) preserves every dwell + scroll while cutting decode+phaseCorr ~3×. `analyze()`
     now advances skipped frames with `cap.grab()` (demux only, no decode) and `retrieve()`s just
     the sampled ones; `select_keyframes()` was rewritten to walk the ordered SAMPLED stats list
     (stride-agnostic: dwell runs, displacement-budget infill, and boundary detection all operate
     on sampled indices, mapping back to REAL frame numbers). Pass-2 keyframe write also switched
     to grab()/retrieve(). Manifest records `analysis_stride`.
     RESULT: task6 ingest ran in **22 s** wall-clock (vs the ~100 s+ Pass-1 era), coverage
     invariant intact (42/42, 0 orphans; Stage A A1/A2/A4/A6 CLEAN). `diff`/`dy` between sampled
     frames = real displacement across the stride gap, exactly what the dwell/budget math needs —
     no correctness change, only fewer frames processed.
  2. dwell threshold STABLE_RUN_MIN kept at 4 but now means 4 *sampled* frames (~0.4 s at stride 3)
     — still well inside a real page pause; no missed pages on task6.
- The comparison crux (5-way): each PSB title page carries "City, State D-D January YYYY"; the
  decisive value per doc is the January START day (first number of the range). Start days:
  2003→3, 2005→4, 2006→3, 2007→3, 2008→4. Set {3,4} ⇒ range 4−3=1; earliest day 3 =
  2003/2006/2007; latest day 4 = 2005/2008 ⇒ option **D**.
- WHY WRONG (first Wrong of the series, and the instructive part): the AI answer was a bare year
  list "2003; 2005; 2006; 2007; 2008" — literally the five years echoed from the question. The
  options are deliberately built so A, B and D all share the SAME year union {2003,2005,2006,2007,
  2008}; only the range value and the earliest/latest ASSIGNMENT differ. So "just list the years"
  disambiguates nothing and answers neither half of the question (range + which-years-earliest/
  latest). It selects no option and is not D ⇒ Wrong. Lesson: on comparison/MC tasks where the
  distractors share an operand set, a year/entity list that merely restates the inputs is a
  non-answer — the verdict turns on whether the AI produced the DERIVED quantity (here range +
  grouping), not on whether the listed items are individually supported. Don't be fooled into
  "Correct" just because every listed token is evidence-backed.
- Quote-integrity (standing rule held): Doc3 (2006) and Doc5 (2008) put CITY and DATE on SEPARATE
  physical lines — quoted the date line ALONE ("3-7 January 2006", "4-8 January 2008"), never
  stitched with the location line. Doc1/Doc2/Doc4 have city+date on one line so the full line is a
  legit single quote. Also: Doc5's date line is on Page 5 because Doc5 P4 = "This page
  intentionally left blank" (note: Doc5 blank reads "intentionally", not "is intentionally" like
  Doc1/Doc4 — copy each verbatim, don't normalize).
- Gate friction: reviewer-simulator REJECT was NOT a quote defect this time (the pre-split rule
  held) — it was a NOTE-completeness gap: the Doc5 Page-5 anchor (an outlier vs everyone else's
  Page 4) looked like a wrong-page/padding error until the note explained "page 4 is blank" + the
  separate-line handling. Lesson: when one citation's page number is an outlier in a cross-doc set,
  the note MUST pre-empt the "why this page?" reviewer reflex. final-evaluator FAIL was a
  deliverable-format gap (for-Suraj block was a self-review, not the DELIVERABLE_TEMPLATE
  Verification summary attesting the gates ran) — fixed and re-SHIPped.
- Open (unchanged): label_tabs auto-skip when tabs supplied; grouping precision; extraction-
  evaluator keyframe-reuse STILL not live-timed (fast path skipped Stage-B by design a 4th
  consecutive task). New: consider making stride adaptive (raise to 4-5 on long/steady recordings,
  drop to 1 if a decisive value sits in a fast scroll) — 3 was safe here but is a fixed guess.

## 2026-07-06 — task6 follow-up: displacement tiling REVERTED (validation caught dropped evidence)

- What happened: acting on Suraj's "cut down so many similar pages / lower tokens" directive, I
  added displacement-based tile emission — emit one tile per ~0.60 viewport scrolled (measured
  from Pass-1 phaseCorrelate dy), aiming to replace the "emit on any change" rule and roughly
  halve the tile count (task6: 65→23 tiles). Then I VALIDATED against task6's known ground truth
  (5 title-page date lines) and found it had SILENTLY DROPPED two decisive values from the tiles:
  Doc1 P4 "Kauai, Hawaii 3-7 January 2003" and Doc4 P4 "Maui, Hawaii 3-7 January 2007" were in no
  emitted tile (the raw keyframes still had them — coverage invariant held — but the readable
  tiles did not).
- Root cause: **displacement gating starves dwells.** A page you PAUSE on accumulates ~0 scroll
  distance, so a "emit every 0.60 viewport of scroll" rule never emits it if the previous tile was
  recent — then a fast scroll to the next page jumps >1 viewport and only the endpoints get tiled,
  leaving the paused page (the most important frame, since that is where the user stopped to read
  the decisive line) with no tile. Fast scrolls also have low phaseCorrelate response, so dy is
  under-counted, compounding the gap.
- Detection gap: none — I caught it because I re-read the tiles nearest each known date line before
  shipping. This is the "cross-check and validate, no mistakes" discipline working: an aggressive
  optimization was proven to drop evidence and was reverted BEFORE it could cause a wrong verdict.
- Change made: **reverted** the tiling to the known-safe "emit at every changed kept frame, dedup
  exact revisits (DUP_DIFF)" logic — every settled page view becomes a readable tile, no gaps
  (`video_pipeline/ingest.py`, tile-emission loop, with a comment recording WHY displacement gating
  is unsafe). Removed EMIT_STRIDE_FRAC + the _cumulative_dy helper. Coverage restored: 39 left
  tiles, frames 135/258 (Doc1 P4) and 795 (Doc4 P4) present, 0 orphans.
- KEPT (safe, validated): the Pass-1 frame-stride sampling (stride 3, grab()/retrieve()) — that is
  the real time win (task6 ingest 22s) and it is coverage-safe because it samples the analysis, not
  the emitted content.
- Rule for future tile-count reduction: it MUST be a content-overlap dedup (drop a tile only when
  its content is provably ⊆ the union of neighbouring kept tiles — i.e. a same-page slight-scroll
  duplicate), gated by a synthetic + all-recordings regression test (task2–6 known decisive values
  must all remain present in tiles). NEVER a scroll-distance stride — that starves dwells. Logged as
  the owned condition before any tiling optimization ships.
- Lower-token lever that IS safe (moved to the DO_TASK side, see system/learning/LESSONS.md same
  date): the per-task token cost is dominated by agent image-reads, addressed by pixel-`src`
  discipline + triangulation (read each decisive value once, confirm from two sources) rather than
  by re-reading many overlapping tiles.
