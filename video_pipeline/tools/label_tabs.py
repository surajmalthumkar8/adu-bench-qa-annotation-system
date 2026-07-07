#!/usr/bin/env python3
"""Annotate ingest tiles with their evidence-tab label via breadcrumb OCR.

Usage:
    python video_pipeline/tools/label_tabs.py <task_dir>

The tab identity of an evidence tile lives in its breadcrumb line
("DocN: <isbn>.pdf — Page Y"). We OCR only a small breadcrumb box, and — since
consecutive tiles in the same tab share an identical breadcrumb — we cache by
pixel-diff so only *distinct* breadcrumbs are actually OCR'd (~7 calls for a
whole task, not one-per-tile; task2 lesson: full-tile OCR of 71 tiles took 155s).

Writes:
  * `tab_label` + authoritative `panel_role` (evidence / form-chrome) onto each
    tile in ingest/manifest.json
  * ingest/tab_groups.json — {tab_label: [ordered tile paths]} so INGEST_VIDEO
    dispatches one doc-reconstructor per tab automatically.

The breadcrumb regex REQUIRES the ".pdf" filename, so the platform's instruction
example text ("Tabs are labeled Doc1 P5, Doc2 P3…") on the form panel does NOT
false-match (task2 lesson: that inverted evidence/form).
RapidOCR (Apache-2.0, CPU/ONNX) only; degrades to a warning if unavailable.
"""

from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

# Require the pdf filename between DocN and Page — real breadcrumbs only.
CRUMB_RE = re.compile(r"(Doc\s*\d)\s*:?\s*\d{9,13}\s*\.?\s*pdf.*?[Pp]age\s*(\d+)")
# Breadcrumb box within a full-height panel tile (fractions of h, w).
BOX = (0.14, 0.25, 0.15, 0.85)   # y0, y1, x0, x1
SAME_BOX_DIFF = 2.0              # mean-abs-diff below which two boxes are "same"


def _load_engine():
    try:
        from rapidocr import RapidOCR
    except ImportError:
        try:
            from rapidocr_onnxruntime import RapidOCR
        except ImportError:
            return None
    return RapidOCR()


def _ocr_join(engine, img) -> str:
    r = engine(img)
    if hasattr(r, "txts") and r.txts is not None:
        return " ".join(r.txts)
    return " ".join(t for _, t, _ in (r[0] or [])) if r and r[0] else ""


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: label_tabs.py <task_dir>")
        return 1
    task = Path(sys.argv[1])
    mpath = task / "ingest" / "manifest.json"
    if not mpath.is_file():
        print(f"FAIL: {mpath} missing — run ingest.py first")
        return 1
    manifest = json.loads(mpath.read_text(encoding="utf-8"))

    engine = _load_engine()
    if engine is None:
        print("WARN: rapidocr not installed — tabs left unlabeled")
        return 2
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("WARN: opencv/numpy not installed")
        return 2

    tiles = [out for seg in manifest.get("segments", [])
             for out in seg.get("outputs", []) if out.get("type") == "stitched_tile"]

    def box_of(out):
        img = cv2.imread(str(task / "ingest" / out["path"]))
        if img is None:
            return None
        h, w = img.shape[:2]
        return img[int(BOX[0] * h):int(BOX[1] * h), int(BOX[2] * w):int(BOX[3] * w)]

    def crumb(box):
        m = CRUMB_RE.search(_ocr_join(engine, box)) if box is not None else None
        return f"{m.group(1).replace(' ', '')} P{m.group(2)}" if m else None

    ocr_calls = 0
    panels = sorted({out.get("panel", "?") for out in tiles})

    # Step 1: find the evidence panel — OCR up to 4 tiles per panel; the panel
    # whose breadcrumb box matches a real DocN…pdf…Page crumb is the evidence
    # side. The form panel is decided by elimination (NO OCR of its 35+ tiles).
    evidence_panel = None
    for panel in panels:
        for out in [o for o in tiles if o.get("panel") == panel][:4]:
            ocr_calls += 1
            if crumb(box_of(out)):
                evidence_panel = panel
                break
        if evidence_panel:
            break

    # Step 2: label only the evidence panel's tiles. Cache by pixel-diff so a run
    # of identical breadcrumbs costs one OCR call, not one per tile.
    last_label = None
    cache_box = cache_label = None
    for out in tiles:
        panel = out.get("panel", "?")
        if panel != evidence_panel:
            out["tab_label"] = None
            continue
        box = box_of(out)
        if box is not None and cache_box is not None and box.shape == cache_box.shape \
                and float(np.mean(np.abs(box.astype(np.float32) -
                                        cache_box.astype(np.float32)))) < SAME_BOX_DIFF:
            label = cache_label
        else:
            ocr_calls += 1
            label = crumb(box)
            cache_box, cache_label = (box.copy() if box is not None else None), label
        if label:
            last_label = label
            out["tab_label"] = label
        else:
            out["tab_label"] = last_label   # inherit within a scroll run
    panel_has_crumb = {p: (p == evidence_panel) for p in panels}

    # Authoritative panel role + grouping (only evidence panels form groups).
    groups: "OrderedDict[str, list[str]]" = OrderedDict()
    for out in tiles:
        panel = out.get("panel", "?")
        is_evidence = panel_has_crumb.get(panel, False)
        out["panel_role"] = "evidence" if is_evidence else "form-chrome"
        if is_evidence:
            lbl = out.get("tab_label") or "unlabeled"
            out["tab_label"] = lbl
            groups.setdefault(lbl, []).append(out["path"])

    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (task / "ingest" / "tab_groups.json").write_text(
        json.dumps(groups, indent=2), encoding="utf-8")

    evidence_panels = [p for p, v in panel_has_crumb.items() if v]
    print(f"{len(tiles)} tiles, {ocr_calls} OCR calls (rest cached); "
          f"evidence panel(s): {evidence_panels}; {len(groups)} tab groups:")
    for lbl, t in groups.items():
        print(f"  {lbl:14} {len(t)} tiles")
    print("\nnext: dispatch one doc-reconstructor per group in ingest/tab_groups.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
