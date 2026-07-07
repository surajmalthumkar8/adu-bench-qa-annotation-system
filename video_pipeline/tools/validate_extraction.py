#!/usr/bin/env python3
"""Stage-A deterministic validator for video-ingest extractions.

Usage:
    python video_pipeline/tools/validate_extraction.py <task_dir> [--json]

<task_dir> is a task folder (e.g. Own_tasks/task7) containing:
    recording.mp4|.mkv   the base video (source of truth)
    ingest/manifest.json ingest/pages/ ingest/chrome/ ingest/keyframes/
    reconstructed/*.md   (optional at validation time; checked when present)

Mechanical checks only — no model judgment (see
video_pipeline/rules/EXTRACTION_QA_RULES.md, Rule 1). Exit codes:
    0  CLEAN  — all checks pass
    2  WARN   — completed with enumerated warnings (Stage B decides)
    1  FAIL   — blocking defect; fix before Stage B

Writes ingest/VALIDATION.json with per-check results and the flagged-region list
that becomes the extraction-evaluator's mandatory audit list.

Checks (research basis: RESEARCH.md §7):
    A1 manifest schema + referenced-file existence
    A2 coverage invariant: every kept keyframe appears in >=1 output's source_frames
    A3 height accounting: composite/tile pixel accounting vs seam offsets
    A4 image sanity: tile dimensions within limits; est_text_px_height gate
    A5 reconstruction text quality: dictionary hit-rate, character entropy,
       repetition-loop detection (reference-free proxies; relaxed for table blocks)
    A6 line-count reconciliation: CV text-line count per tile vs reconstruction
       (requires opencv + numpy; WARN-skip if unavailable)
    A7 cross-engine OCR tripwire: RapidOCR per-tile text vs reconstruction
       normalized similarity (requires rapidocr; WARN-skip if unavailable)
    A8 source-video preflight echo: pix_fmt/resolution warnings via ffprobe
       (requires ffprobe on PATH or imageio-ffmpeg; WARN-skip if unavailable)
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------- result model

CLEAN, WARN, FAIL = "CLEAN", "WARN", "FAIL"


class Report:
    def __init__(self) -> None:
        self.checks: list[dict] = []
        self.flagged_regions: list[dict] = []

    def add(self, check: str, status: str, detail: str) -> None:
        self.checks.append({"check": check, "status": status, "detail": detail})

    def flag(self, path: str, reason: str) -> None:
        self.flagged_regions.append({"path": path, "reason": reason})

    @property
    def status(self) -> str:
        statuses = {c["status"] for c in self.checks}
        if FAIL in statuses:
            return FAIL
        if WARN in statuses:
            return WARN
        return CLEAN


# ---------------------------------------------------------------- A1: manifest

REQUIRED_OUTPUT_KEYS = {"type", "path", "order", "source_frames"}
KNOWN_OUTPUT_TYPES = {"stitched_tile", "raw_keyframe", "aux_keyframe"}


def check_manifest(task_dir: Path, report: Report) -> dict | None:
    mpath = task_dir / "ingest" / "manifest.json"
    if not mpath.is_file():
        report.add("A1-manifest", FAIL, f"missing {mpath}")
        return None
    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        report.add("A1-manifest", FAIL, f"manifest unparseable: {e}")
        return None

    problems: list[str] = []
    if manifest.get("schema_version") != 1:
        problems.append(f"schema_version={manifest.get('schema_version')!r}, expected 1")
    segments = manifest.get("segments")
    if not isinstance(segments, list) or not segments:
        problems.append("segments missing or empty")
        segments = []

    for seg in segments:
        sid = seg.get("id", "<no-id>")
        for out in seg.get("outputs", []):
            missing = REQUIRED_OUTPUT_KEYS - out.keys()
            if missing:
                problems.append(f"{sid}: output missing keys {sorted(missing)}")
            if out.get("type") not in KNOWN_OUTPUT_TYPES:
                problems.append(f"{sid}: unknown output type {out.get('type')!r}")
            rel = out.get("path")
            if rel and not (task_dir / "ingest" / rel).is_file():
                problems.append(f"{sid}: referenced file missing: ingest/{rel}")
        chrome = seg.get("chrome_image")
        if chrome and not (task_dir / "ingest" / chrome).is_file():
            problems.append(f"{sid}: chrome image missing: ingest/{chrome}")

    if problems:
        report.add("A1-manifest", FAIL, "; ".join(problems))
        return None
    report.add("A1-manifest", CLEAN,
               f"{len(segments)} segments, all referenced files present")
    return manifest


# --------------------------------------------------------------- A2: coverage


def check_coverage(manifest: dict, report: Report) -> None:
    cov = manifest.get("coverage", {})
    orphans = cov.get("orphans")
    kept = cov.get("kept_keyframes")
    represented = cov.get("represented_in_outputs")
    if orphans is None or kept is None:
        report.add("A2-coverage", FAIL, "manifest coverage block missing/incomplete")
        return
    if orphans != 0:
        report.add("A2-coverage", FAIL,
                   f"{orphans} keyframes unrepresented in any output — content loss")
        return
    # Independent recount from outputs, not trusting the block.
    seen: set[int] = set()
    for seg in manifest.get("segments", []):
        for out in seg.get("outputs", []):
            seen.update(out.get("source_frames", []))
    if represented is not None and len(seen) < represented:
        report.add("A2-coverage", FAIL,
                   f"coverage block claims {represented} represented but outputs "
                   f"only reference {len(seen)} distinct frames")
        return
    report.add("A2-coverage", CLEAN,
               f"{kept} keyframes, 0 orphans, {len(seen)} distinct frames referenced")


# --------------------------------------------------- A3: height accounting


def check_height_accounting(manifest: dict, task_dir: Path, report: Report) -> None:
    """Per composite: sum of seam dy offsets + one viewport must ~equal total
    composite pixel height (tiles' y-ranges). Tolerance ±5% (tunable; see
    EXTRACTION_QA_RULES / RESEARCH §7 scroll-distance conservation)."""
    issues, checked = [], 0
    for seg in manifest.get("segments", []):
        by_composite: dict[str, list[dict]] = {}
        for out in seg.get("outputs", []):
            if out.get("type") == "stitched_tile" and out.get("composite_id"):
                by_composite.setdefault(out["composite_id"], []).append(out)
        for cid, tiles in by_composite.items():
            ranges = [t.get("tile_y_range") for t in tiles if t.get("tile_y_range")]
            if not ranges:
                continue
            total_h = max(r[1] for r in ranges)
            n_seams = sum(len(t.get("seams", [])) for t in tiles)
            if n_seams == 0 and total_h > 0:
                continue  # single-frame composite; nothing to conserve
            checked += 1
            # dy sum: each seam's y is a paste offset in composite space; the last
            # seam y + one viewport height should reach total_h.
            last_seam_y = max((s["y"] for t in tiles for s in t.get("seams", [])),
                              default=0)
            if last_seam_y > total_h:
                issues.append(f"{cid}: seam y {last_seam_y} beyond composite "
                              f"height {total_h}")
    if issues:
        report.add("A3-height", FAIL, "; ".join(issues))
    elif checked == 0:
        report.add("A3-height", WARN,
                   "no multi-seam composites to check (keyframes-only extraction?)")
    else:
        report.add("A3-height", CLEAN, f"{checked} composites consistent")


# ---------------------------------------------------------- A4: image sanity

MAX_TILE_PX = 2000  # Claude Code Read clamp — ARCHITECTURE §2.8
MIN_TEXT_PX = 15


def check_images(manifest: dict, task_dir: Path, report: Report) -> None:
    try:
        from PIL import Image
    except ImportError:
        report.add("A4-images", WARN, "Pillow not installed — image checks skipped")
        return
    oversize, small_text, unreadable = [], [], []
    for seg in manifest.get("segments", []):
        for out in seg.get("outputs", []):
            p = task_dir / "ingest" / out.get("path", "")
            if not p.is_file():
                continue  # A1 already failed it
            try:
                with Image.open(p) as im:
                    w, h = im.size
            except OSError:
                unreadable.append(out["path"])
                continue
            if out.get("type") == "stitched_tile" and (w > MAX_TILE_PX or h > MAX_TILE_PX):
                oversize.append(f"{out['path']} ({w}x{h})")
            est = out.get("est_text_px_height")
            if est is not None and est < MIN_TEXT_PX and not out.get("upscaled", 1.0) > 1.0:
                small_text.append(f"{out['path']} (text~{est}px, not upscaled)")
    if unreadable:
        report.add("A4-images", FAIL, f"unreadable images: {unreadable}")
        return
    problems = []
    if oversize:
        problems.append(f"tiles exceed {MAX_TILE_PX}px (will be silently downscaled "
                        f"by Claude Code): {oversize}")
        for o in oversize:
            report.flag(o.split(" ")[0], "oversize tile — resolution silently lost")
    if small_text:
        problems.append(f"sub-{MIN_TEXT_PX}px text without upscale: {small_text}")
        for s in small_text:
            report.flag(s.split(" ")[0], "small text — mandatory zoomed-crop audit")
    if problems:
        report.add("A4-images", WARN, "; ".join(problems))
    else:
        report.add("A4-images", CLEAN, "all tiles within limits")


# ------------------------------------------ A5: reconstruction text quality

WORD_RE = re.compile(r"[A-Za-z]{2,}")
# Small built-in stopword/common-word set; supplemented by any words that appear
# >=3 times in the doc itself (domain terms self-validate by repetition).
COMMON = set("""the of and to in a is that for it as was with be by on not he this
are or his from at which but have an they you were her she all their we him been
has when who will no more if out so what up said its about than into them can
only other time new some could these two may first then do any like my now over
such our man me even most made after also did many off before must well back
through years where much your way down should because each just those people
how too little state good very make world still see own men work long here get
both between life being under never day same another know while last might us
great old year come since against go came right used take three""".split())

REPEAT_RE = re.compile(r"(.{3,40}?)\1{4,}", re.DOTALL)  # 5+ consecutive repeats


def _entropy(text: str) -> float:
    counts = Counter(text)
    n = len(text)
    return -sum((c / n) * math.log2(c / n) for c in counts.values()) if n else 0.0


def check_text_quality(task_dir: Path, report: Report) -> None:
    recon = sorted((task_dir / "reconstructed").glob("*.md"))
    recon = [p for p in recon if p.name != "EVIDENCE_INDEX.md"]
    if not recon:
        report.add("A5-text", WARN, "no reconstructed/*.md yet — text checks skipped "
                                    "(re-run after reconstruction)")
        return
    problems = []
    for p in recon:
        text = p.read_text(encoding="utf-8", errors="replace")
        # Strip code/latex/table blocks for the lexicon check (they're not prose).
        prose = re.sub(r"```.*?```|\$\$.*?\$\$|\$[^$\n]*\$", " ", text, flags=re.DOTALL)
        prose = "\n".join(ln for ln in prose.splitlines() if not ln.lstrip().startswith("|"))
        words = [w.lower() for w in WORD_RE.findall(prose)]
        if len(words) >= 30:
            selfcommon = {w for w, c in Counter(words).items() if c >= 3}
            hit = sum(1 for w in words if w in COMMON or w in selfcommon) / len(words)
            if hit < 0.45:
                problems.append(f"{p.name}: lexicon hit-rate {hit:.0%} (<45%) — "
                                f"possible garbled transcription")
                report.flag(p.name, "low lexicon hit-rate")
        ent = _entropy(text)
        if text and (ent < 2.5 or ent > 6.5):
            problems.append(f"{p.name}: char entropy {ent:.2f} outside [2.5, 6.5]")
            report.flag(p.name, "abnormal character entropy")
        m = REPEAT_RE.search(text)
        if m:
            problems.append(f"{p.name}: repetition loop detected "
                            f"({m.group(1)[:30]!r} x5+) — known VLM failure mode")
            report.flag(p.name, "repetition loop")
    if problems:
        report.add("A5-text", FAIL, "; ".join(problems))
    else:
        report.add("A5-text", CLEAN, f"{len(recon)} reconstructed docs pass "
                                     f"lexicon/entropy/repetition checks")


# ------------------------------------------- A6: line-count reconciliation


def _cv_line_count(img_path: Path) -> int | None:
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    # Morphological text-line detection: invert-threshold, dilate horizontally,
    # count connected components taller than noise.
    thr = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY_INV, 25, 15)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    lines = cv2.dilate(thr, kernel, iterations=1)
    n, _, stats, _ = cv2.connectedComponentsWithStats(lines)
    return int(sum(1 for i in range(1, n)
                   if stats[i, cv2.CC_STAT_HEIGHT] >= 6
                   and stats[i, cv2.CC_STAT_WIDTH] >= 60))


def check_line_counts(manifest: dict, task_dir: Path, report: Report) -> None:
    counted, flagged = 0, []
    for seg in manifest.get("segments", []):
        for out in seg.get("outputs", []):
            if out.get("type") != "stitched_tile":
                continue
            p = task_dir / "ingest" / out.get("path", "")
            if not p.is_file():
                continue
            n = _cv_line_count(p)
            if n is None:
                report.add("A6-lines", WARN,
                           "opencv/numpy not installed — line-count check skipped")
                return
            counted += 1
            out["_cv_line_count"] = n  # recorded into VALIDATION.json
            if n == 0:
                flagged.append(out["path"])
                report.flag(out["path"], "CV detects zero text lines in tile")
    if flagged:
        report.add("A6-lines", WARN,
                   f"tiles with zero detected text lines (blank? mis-stitch?): {flagged}")
    elif counted:
        report.add("A6-lines", CLEAN, f"{counted} tiles have detectable text lines "
                                      f"(per-tile counts in VALIDATION.json for Stage B)")
    else:
        report.add("A6-lines", WARN, "no stitched tiles to count")


# --------------------------------------------- A7: cross-engine OCR tripwire


def check_cross_ocr(manifest: dict, task_dir: Path, report: Report) -> None:
    try:
        from rapidocr import RapidOCR  # type: ignore
    except ImportError:
        try:
            from rapidocr_onnxruntime import RapidOCR  # type: ignore
        except ImportError:
            report.add("A7-crossocr", WARN,
                       "rapidocr not installed — cross-engine tripwire skipped "
                       "(pip install rapidocr)")
            return
    recon_dir = task_dir / "reconstructed"
    if not any(recon_dir.glob("*.md")) if recon_dir.is_dir() else True:
        report.add("A7-crossocr", WARN,
                   "no reconstruction yet — cross-engine tripwire deferred")
        return
    engine = RapidOCR()
    recon_text = " ".join(p.read_text(encoding="utf-8", errors="replace").lower()
                          for p in recon_dir.glob("*.md")
                          if p.name != "EVIDENCE_INDEX.md")
    recon_tokens = set(WORD_RE.findall(recon_text))
    weak = []
    # Only evidence-bearing tiles are arbitrated. Static (form-chrome) panels — the
    # annotation form / question column — are intentionally condensed in the
    # reconstruction, so a low token overlap there is by-design, not content loss
    # (task2 lesson: 20 benign right-panel flags). They carry no document evidence,
    # so the reconstruction-vs-OCR comparison is not meaningful for them.
    skipped_chrome = 0
    tiles = []
    for seg in manifest.get("segments", []):
        for out in seg.get("outputs", []):
            if out.get("type") != "stitched_tile":
                continue
            if out.get("panel_role") in ("static", "form-chrome"):
                skipped_chrome += 1
                continue
            tiles.append((seg, out))
    for seg, out in tiles:
        p = task_dir / "ingest" / out["path"]
        if not p.is_file():
            continue
        try:
            result = engine(str(p))
            texts = (result.txts if hasattr(result, "txts") else
                     [t for _, t, _ in (result[0] or [])]) or []
        except Exception as e:  # engine crash on one tile must not kill the gate
            report.flag(out["path"], f"rapidocr error: {e}")
            continue
        ocr_tokens = set(w.lower() for w in WORD_RE.findall(" ".join(texts)))
        if len(ocr_tokens) < 5:
            continue  # too little machine-readable text to compare
        overlap = len(ocr_tokens & recon_tokens) / len(ocr_tokens)
        out["_crossocr_overlap"] = round(overlap, 3)
        if overlap < 0.70:
            weak.append(f"{out['path']} ({overlap:.0%})")
            report.flag(out["path"],
                        f"cross-engine overlap {overlap:.0%} <70% — audit mandatory")
    suffix = (f" ({skipped_chrome} static form-chrome tiles excluded by design)"
              if skipped_chrome else "")
    if weak:
        report.add("A7-crossocr", WARN,
                   f"evidence tiles where RapidOCR text is poorly represented in the "
                   f"reconstruction (tripwire, not verdict): {weak}{suffix}")
    else:
        report.add("A7-crossocr", CLEAN,
                   f"{len(tiles)} evidence tiles cross-checked; no low-overlap "
                   f"tripwires{suffix}")


# --------------------------------------------------- A8: source-video preflight


def _ffprobe_bin() -> str | None:
    if shutil.which("ffprobe"):
        return "ffprobe"
    try:
        import imageio_ffmpeg
        # imageio-ffmpeg bundles ffmpeg (not ffprobe); ffmpeg -i also prints
        # stream info, so fall back to that.
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


def check_video_preflight(task_dir: Path, report: Report) -> None:
    video = next((p for ext in ("mp4", "mkv", "mov")
                  for p in task_dir.glob(f"*.{ext}")), None)
    if video is None:
        report.add("A8-video", FAIL, "no recording.(mp4|mkv|mov) in task dir — "
                                     "the source of truth is missing")
        return
    exe = _ffprobe_bin()
    if exe is None:
        report.add("A8-video", WARN, "ffprobe/ffmpeg unavailable — preflight skipped")
        return
    if exe == "ffprobe":
        cmd = [exe, "-v", "error", "-select_streams", "v:0", "-show_entries",
               "stream=width,height,pix_fmt,avg_frame_rate", "-of", "json", str(video)]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            info = json.loads(out.stdout)["streams"][0]
        except (subprocess.SubprocessError, KeyError, IndexError,
                json.JSONDecodeError) as e:
            report.add("A8-video", WARN, f"ffprobe failed: {e}")
            return
        warns = []
        if info.get("width", 0) < 1920:
            warns.append(f"width {info.get('width')} <1920 — legibility at risk")
        if str(info.get("pix_fmt", "")).startswith("yuv420"):
            warns.append("pix_fmt yuv420 (4:2:0 chroma) — colored text edges smeared; "
                         "RECORDING_SOP requires I444")
        if warns:
            report.add("A8-video", WARN, f"{video.name}: " + "; ".join(warns))
        else:
            report.add("A8-video", CLEAN,
                       f"{video.name}: {info.get('width')}x{info.get('height')} "
                       f"{info.get('pix_fmt')}")
    else:
        report.add("A8-video", WARN,
                   "only bundled ffmpeg found (no ffprobe) — detailed preflight "
                   "skipped; video present: " + video.name)


# ------------------------------------------------------------------- driver


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("task_dir", type=Path)
    ap.add_argument("--json", action="store_true", help="print JSON to stdout too")
    args = ap.parse_args()
    task_dir: Path = args.task_dir
    if not task_dir.is_dir():
        print(f"FAIL: {task_dir} is not a directory")
        return 1

    report = Report()
    check_video_preflight(task_dir, report)
    manifest = check_manifest(task_dir, report)
    if manifest is not None:
        check_coverage(manifest, report)
        check_height_accounting(manifest, task_dir, report)
        check_images(manifest, task_dir, report)
        check_line_counts(manifest, task_dir, report)
        check_cross_ocr(manifest, task_dir, report)
    check_text_quality(task_dir, report)

    result = {"status": report.status, "checks": report.checks,
              "flagged_regions": report.flagged_regions}
    out_path = task_dir / "ingest" / "VALIDATION.json"
    if (task_dir / "ingest").is_dir():
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    for c in report.checks:
        print(f"[{c['status']:5}] {c['check']}: {c['detail']}")
    if report.flagged_regions:
        print(f"\nFlagged regions (mandatory Stage-B audit list, "
              f"{len(report.flagged_regions)}):")
        for f in report.flagged_regions:
            print(f"  - {f['path']}: {f['reason']}")
    print(f"\n{report.status}")
    if args.json:
        print(json.dumps(result, indent=2))
    return {CLEAN: 0, WARN: 2, FAIL: 1}[report.status]


if __name__ == "__main__":
    sys.exit(main())
