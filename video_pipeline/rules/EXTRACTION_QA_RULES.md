# EXTRACTION_QA_RULES — binding rules for the video-extraction QA gate

These rules govern the COMPULSORY quality gate between "pipeline produced an
extraction" and "extraction may feed DO_TASK". They bind the orchestrator, the
`extraction-evaluator` agent, and any repair loop. Research basis: RESEARCH.md §7–8.

## Rule 0 — The base video is the source of truth

Not the manifest, not the tiles, not the reconstruction. Any disagreement at any
level is resolved by extracting and reading the exact frame from the recording
(`ffmpeg -i recording.mp4 -ss <t> -frames:v 1 ...`, `-ss` after `-i` for frame
accuracy). If the pixels aren't in the video, the content does not exist for this
system — and if pixels ARE in the video, losing them anywhere downstream is a defect.

## Rule 1 — Two-stage gate, both compulsory, in order

- **Stage A — deterministic validator** (`python video_pipeline/tools/validate_extraction.py <task_dir>`).
  Mechanical, code-only, no model judgment. Must print CLEAN (exit 0) or
  WARN (exit 2, with every warning enumerated). FAIL (exit 1) blocks Stage B —
  fix the pipeline output first.
- **Stage B — extraction-evaluator agent** (`.claude/agents/extraction-evaluator.md`).
  Vision audit against the base video. Must return PASS.

No extraction reaches DO_TASK without Stage A CLEAN/WARN **and** Stage B PASS.
This mirrors the annotation system's own gate chain (validator CLEAN →
reviewer-simulator APPROVE) — same philosophy, applied to extraction.

## Rule 2 — Perception, not preference (anti-self-judging)

The evaluator is the same model family that produced the reconstruction;
self-preference bias is measured, survives anonymization, and skews lenient.
Therefore every evaluator verdict must come from **blind independent
re-transcription of the source image, then a mechanical diff** — never from reading
the reconstruction and forming an opinion about it. Checklist verdicts with cited
evidence per item; holistic scores are forbidden.

## Rule 3 — Sampling floor (C=0 acceptance sampling)

Beyond the mandatory audit list (all flagged regions, all decisive values, all
`[UNREADABLE]`/`[CONTINUES]` markers), the evaluator audits **≥30 randomly drawn
units with ZERO content-loss defects** (95% confidence miss-rate <10%; use 60 units
for <5% on high-stakes tasks). Units are drawn by manifest coordinates before any
content is viewed, stratified across segments, oversampling high-scroll-velocity
stretches. The unit list is logged (SAMPLE_LOG) so re-runs draw fresh samples.

## Rule 4 — Defect classes and what blocks

| Class | Definition | Blocks? |
|---|---|---|
| CONTENT_LOSS | Anything visible in a sampled frame absent from every output image or the reconstruction | YES — always |
| VALUE_ERROR | Any character wrong in a decisive value (numbers, ISBNs, option letters, table cells) | YES — always |
| STRUCTURE_ERROR | Table cell placement, reading order, equation structure wrong | YES unless demonstrably immaterial to the task |
| FORMATTING_NOISE | Whitespace, markdown syntax, hyphenation, line-wrap differences | Never |

## Rule 5 — The repair loop (bounded, targeted, monotone)

Naive "loop until pass" degrades output — repair only on concrete external evidence:

1. **Targeted repair only.** Re-transcribe/re-process ONLY the failing regions, with
   the evaluator's evidence (frame crops, diff hunks) in the repair context. Full
   re-extraction is forbidden unless Stage A failed structurally (it risks regressing
   correct regions).
2. **Max 3 iterations.** Iteration = repair + full Stage A re-run + Stage B on
   (repaired regions + a FRESH random sample).
3. **Monotone improvement required.** Track the defect count per iteration. If an
   iteration does not strictly reduce defects, STOP — do not iterate again.
4. **Keep the best-ever version**, not the last one.
5. **Escalate on exhaustion.** 3 iterations without PASS, or any non-improving
   iteration ⇒ STOP and present Suraj the evidence bundle (failing regions, frames,
   diffs) with a concrete ask: re-record the failing stretch, or paste a screenshot
   of the specific region, or confirm the content is immaterial. Never ship a
   known-defective extraction into DO_TASK, and never silently accept one.

## Rule 6 — Zero-cost / zero-exfiltration constraints (binding)

- **No external LLM APIs.** All model work is Claude in-session (Claude Code).
- **No portal access.** The system never logs into Feather/Henna to fetch documents;
  the recording is the only input.
- **Open-source CPU tools only** for mechanical checks: ffmpeg/ffprobe, OpenCV,
  RapidOCR (Apache-2.0, decorrelated OCR cross-check), optionally Tesseract 5.
  A classical OCR engine disagreeing with Claude is a strong free signal — but the
  classical engine is a TRIPWIRE (flags disagreement for audit), never the arbiter.
- **No MCP servers for this pipeline** — inside Claude Code, Bash + Python already
  provide full ffmpeg/OCR/imaging control; MCP wrappers add config surface, not
  capability (RESEARCH §8).

## Rule 7 — Learning loop (mandatory)

Every Stage A/Stage B failure, every escalation, and every defect that survives to
DO_TASK or to a platform reviewer ⇒ append an entry to
`video_pipeline/learning/LESSONS.md` (what failed, root cause, which rule/threshold/
check changed in response) AND update the affected rule, config default, or agent
instruction in the same session. A defect class that has been seen once must be
mechanically detectable (Stage A) or explicitly audited (Stage B) thereafter.

## Rule 8 — Honest reporting

Stage results are reported verbatim: warnings enumerated, sample sizes stated,
defects shown with evidence. "PASS (30 units audited, 0 defects, 2 formatting
diffs ignored)" — never just "looks good". If a check could not run (missing
dependency, missing file), that is a WARN with the reason, never a silent skip.
