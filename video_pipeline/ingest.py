#!/usr/bin/env python3
"""MVP video-ingest CLI — keyframes-only fallback mode (no stitching yet).

Usage:
    python video_pipeline/ingest.py <recording> --out <task_dir> [options]

Implements the ARCHITECTURE.md pipeline in its sanctioned degraded form
(PROJECT_PLAN goal 3): every piece of content the recording shows is emitted as
overlapping keyframes + per-panel tiles; nothing is stitched. Worst case equals
the manual-screenshot workflow, never worse. Stitching lands in Phase 1 proper.

Stages:
  1. Pass 1 (analysis): decode all frames at 1/4-scale grayscale; per-frame
     motion stats (mean-abs-diff + phase-correlation dy).
  2. Keyframe selection: last-frame-of-dwell for every stable run, PLUS
     displacement-budget infill so no scroll stretch exceeds ~40% viewport.
  3. Pass 2 (emission): write full raw keyframes (coverage guarantee), then
     classify each panel as scroll vs static and emit tiles accordingly —
     a near-static panel (the Q/A form) yields only its distinct states instead
     of one tile per dwell (task2 lesson: ~40 redundant right tiles → ~2-3).
     Manifest tags every tile with panel + panel_role so downstream QA can skip
     form chrome and reconstruction can auto-group. Coverage gate enforced.

Exit codes: 0 ok, 1 hard failure, 2 completed with warnings.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ANALYSIS_SCALE = 0.25          # 1/4-scale grayscale for motion stats
# Frame stride for Pass 1 analysis. Screen recordings dwell on each page for
# ~1 s, so sampling every 3rd frame (10 fps @ 30 fps source) preserves every
# dwell + scroll and cuts the phaseCorrelate cost (the pipeline's bottleneck)
# ~3x. Skipped frames are demuxed-not-decoded via cap.grab() (task6 speed pass).
ANALYSIS_STRIDE = 3
STABLE_DIFF = 1.2              # mean-abs-diff below this => "no motion" (0-255)
STABLE_RUN_MIN = 4             # sampled frames of stability that define a dwell
CONTENT_CHANGE = 18.0          # mean-abs-diff above this => hard content change
DISPLACEMENT_BUDGET = 0.40     # max viewport fraction scrolled between keeps
MIN_PHASE_RESPONSE = 0.15      # below this, phase-corr dy is untrusted
PANEL_OVERLAP_PX = 80          # horizontal overlap so no glyph splits at the seam

# Tile-emission thresholds (mean-abs-diff on 1/4-scale panel crops).
# Raised from the first cut (1.0) so caret blink / sub-pixel scroll don't force a
# fresh tile — the #1 source of redundant right-panel tiles on task2.
TILE_CHANGE = 3.0
# A panel that changes in fewer than this fraction of kept keyframes is "static"
# (the annotation form / question column). Static panels emit only distinct
# states, capped, instead of one tile per dwell.
STATIC_PANEL_FRAC = 0.30
STATIC_PANEL_CAP = 4
# Global (not just adjacent) near-identical dedup: a candidate tile that matches
# ANY already-emitted tile of the same panel below this mean-abs-diff is a
# scroll-back revisit of content we already have — skip it. Kept tight so only
# pixel-near-identical revisits drop; distinct pages differ by >> this. Coverage
# stays intact because every kept frame is still represented by its raw_keyframe.
DUP_DIFF = 1.5


def log(msg: str) -> None:
    print(msg, flush=True)


# --------------------------------------------------------------- pass 1: stats

def analyze(video: Path, stride: int = ANALYSIS_STRIDE):
    """Motion stats on every `stride`-th frame at 1/4 scale. Returns (stats, meta).

    Skipped frames are advanced with cap.grab() (demux only, no decode) so only
    sampled frames pay the decode + phaseCorrelate cost. `diff`/`dy` are measured
    between consecutive SAMPLED frames — i.e. real displacement across the stride
    gap, which is exactly what the dwell/displacement logic needs.
    """
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise SystemExit(f"FAIL: cannot open {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    stats = []
    prev = None
    w = h = None
    i = -1
    while True:
        if not cap.grab():
            break
        i += 1
        if i % stride != 0:
            continue
        ok, frame = cap.retrieve()
        if not ok:
            break
        if w is None:
            h, w = frame.shape[:2]
        g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(g, None, fx=ANALYSIS_SCALE, fy=ANALYSIS_SCALE,
                           interpolation=cv2.INTER_AREA).astype(np.float32)
        if prev is not None:
            diff = float(np.mean(np.abs(small - prev)))
            (dx, dy), resp = cv2.phaseCorrelate(prev, small)
            stats.append({"i": i, "diff": diff,
                          "dy": float(dy) / ANALYSIS_SCALE,
                          "dx": float(dx) / ANALYSIS_SCALE,
                          "resp": float(resp)})
        prev = small
    cap.release()
    return stats, {"frames": i + 1, "fps": fps, "width": w, "height": h,
                   "stride": stride}


# ------------------------------------------------------ keyframe selection

def select_keyframes(stats, meta):
    """Dwell ends + displacement-budget infill over the SAMPLED sequence.

    Works on the ordered `stats` list (one entry per sampled frame) rather than
    every real index, so it is stride-agnostic. Returns (kept_idx, boundaries)
    where indices are REAL frame numbers.
    """
    h = meta["height"]
    if not stats:
        raise SystemExit("FAIL: zero frames decoded")
    idxs = [s["i"] for s in stats]          # real frame indices, ordered
    diff_of = {s["i"]: s for s in stats}

    kept: list[int] = []
    run_start = 0                            # position within `stats`
    for pos in range(1, len(stats)):
        if stats[pos]["diff"] > STABLE_DIFF:  # moving
            if pos - run_start >= STABLE_RUN_MIN:
                kept.append(stats[pos - 1]["i"])
            run_start = pos
    if len(stats) - run_start >= 1:
        kept.append(stats[-1]["i"])
    if not kept or kept[0] != 0:
        kept.insert(0, 0)                    # frame 0 always anchors coverage

    budget_px = DISPLACEMENT_BUDGET * h
    infill: list[int] = []
    for a, b in zip(kept, kept[1:]):
        cum = 0.0
        for ix in (x for x in idxs if a < x <= b):
            s = diff_of[ix]
            if s["resp"] >= MIN_PHASE_RESPONSE and abs(s["dx"]) < 40:
                cum += abs(s["dy"])
            elif s["diff"] > CONTENT_CHANGE:
                cum = 0.0
            if cum >= budget_px and ix < b:
                infill.append(ix)
                cum = 0.0
    kept = sorted(set(kept) | set(infill))

    boundaries: set[int] = {kept[0]}
    for a, b in zip(kept, kept[1:]):
        for ix in (x for x in idxs if a < x <= b):
            s = diff_of[ix]
            if s["diff"] > CONTENT_CHANGE and s["resp"] < MIN_PHASE_RESPONSE:
                boundaries.add(b)
                break
    return kept, boundaries


# ------------------------------------------------------------ pass 2: emit

def _est_text_px(gray) -> int | None:
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY_INV, 25, 15)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    lines = cv2.dilate(thr, kernel, iterations=1)
    cnt, _, cc, _ = cv2.connectedComponentsWithStats(lines)
    heights = [int(cc[i, cv2.CC_STAT_HEIGHT]) for i in range(1, cnt)
               if cc[i, cv2.CC_STAT_HEIGHT] >= 6 and cc[i, cv2.CC_STAT_WIDTH] >= 60]
    return int(np.median(heights)) if heights else None


def _panel_small(crop):
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    return cv2.resize(g, None, fx=0.25, fy=0.25,
                      interpolation=cv2.INTER_AREA).astype(np.float32)


def emit(video: Path, out_dir: Path, kept, boundaries, meta, split_x):
    ingest = out_dir / "ingest"
    for sub in ("keyframes", "pages", "chrome"):
        (ingest / sub).mkdir(parents=True, exist_ok=True)

    panels = [("left", 0, min(split_x + PANEL_OVERLAP_PX, meta["width"])),
              ("right", max(split_x - PANEL_OVERLAP_PX, 0), meta["width"])]

    # ---- single video decode: write raw keyframes, buffer panel thumbnails ----
    cap = cv2.VideoCapture(str(video))
    kept_set = set(kept)
    kf_path: dict[int, str] = {}
    panel_small: dict[str, dict[int, np.ndarray]] = {"left": {}, "right": {}}
    i = -1
    while True:
        if not cap.grab():          # demux only; decode just the kept frames
            break
        i += 1
        if i not in kept_set:
            continue
        ok, frame = cap.retrieve()
        if not ok:
            break
        rel = f"keyframes/f{i:05d}.png"
        cv2.imwrite(str(ingest / rel), frame)
        kf_path[i] = rel
        for name, x0, x1 in panels:
            panel_small[name][i] = _panel_small(frame[:, x0:x1])
    cap.release()

    # ---- classify each panel: scroll (evidence) vs static (form chrome) ----
    roles: dict[str, str] = {}
    for name, _, _ in panels:
        smalls = [panel_small[name][k] for k in kept]
        changes = sum(1 for a, b in zip(smalls, smalls[1:])
                      if a.shape == b.shape and float(np.mean(np.abs(a - b))) > TILE_CHANGE)
        frac = changes / max(1, len(smalls) - 1)
        roles[name] = "static" if frac < STATIC_PANEL_FRAC else "scroll"

    # ---- decide which (frame, panel) tiles to emit ----
    # Emit a tile at every kept frame whose panel content changed vs the previous
    # emitted tile (>TILE_CHANGE), deduping only exact scroll-back revisits
    # (DUP_DIFF). This keeps EVERY settled page view — a dwell accumulates no
    # scroll distance, so displacement-based gating would starve it and drop the
    # very page you paused to read (task6: a 0.60-viewport stride silently dropped
    # the Doc1 P4 and Doc4 P4 date lines from the tiles). Safe-by-default: every
    # decisive value stays present in a readable tile. Tile-count reduction is
    # deferred to a test-harness-gated content-overlap dedup (see LESSONS 2026-07-06
    # task6-followup) so it can never re-introduce that coverage gap.
    emit_set: dict[str, list[int]] = {"left": [], "right": []}
    dropped_dups: dict[str, int] = {"left": 0, "right": 0}
    for name, _, _ in panels:
        prev = None
        chosen: list[int] = []
        emitted: list[np.ndarray] = []   # signatures of tiles already kept
        for k in kept:
            s = panel_small[name][k]
            is_step = prev is None or prev.shape != s.shape or \
                float(np.mean(np.abs(s - prev))) > TILE_CHANGE
            if not is_step:
                continue
            prev = s
            # global dedup: skip scroll-back revisits of already-emitted content
            if any(e.shape == s.shape and float(np.mean(np.abs(s - e))) < DUP_DIFF
                   for e in emitted):
                dropped_dups[name] += 1
                continue
            chosen.append(k)
            emitted.append(s)
        if roles[name] == "static":
            chosen = chosen[:STATIC_PANEL_CAP]  # distinct form states only
        emit_set[name] = chosen

    # ---- build segments + write tiles by re-reading the saved keyframes ----
    seg_of: dict[int, dict] = {}
    segments: list[dict] = []
    seg_no = 0
    order = 0
    warnings: list[str] = []
    for k in kept:
        if not segments or k in boundaries:
            seg_no += 1
            seg = {"id": f"seg{seg_no:02d}", "content_hint": None,
                   "chrome_image": None, "outputs": []}
            segments.append(seg)
        seg_of[k] = segments[-1]
        segments[-1]["outputs"].append({
            "type": "raw_keyframe", "path": kf_path[k], "order": order,
            "source_frames": [k]})
        order += 1

    for name, x0, x1 in panels:
        for k in emit_set[name]:
            full = cv2.imread(str(ingest / kf_path[k]))
            crop = full[:, x0:x1]
            g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            rel = f"pages/f{k:05d}_{name}.png"
            cv2.imwrite(str(ingest / rel), crop)
            th, tw = crop.shape[:2]
            if tw > 2000 or th > 2000:
                warnings.append(f"{rel} is {tw}x{th} — exceeds 2000px")
            seg_of[k]["outputs"].append({
                "type": "stitched_tile", "path": rel, "order": order,
                "source_frames": [k], "composite_id": f"{seg_of[k]['id']}_{name}",
                "tile_y_range": [0, th], "seams": [],
                "est_text_px_height": _est_text_px(g),
                "panel": name, "panel_role": roles[name]})
            order += 1

    # ---- chrome (tab bar) from the first kept frame's left panel ----
    first = cv2.imread(str(ingest / kf_path[kept[0]]))
    band = first[0:int(meta["height"] * 0.30), 0:split_x]
    cv2.imwrite(str(ingest / "chrome" / "tabbar.png"), band)
    segments[0]["chrome_image"] = "chrome/tabbar.png"

    represented = set(kf_path.keys())
    orphans = len(kept_set - represented)
    manifest = {
        "schema_version": 1,
        "video": {"file": video.name, "frames": meta["frames"], "fps": meta["fps"],
                  "width": meta["width"], "height": meta["height"],
                  "decoded_frames": meta["frames"],
                  "analysis_stride": meta.get("stride", 1), "split_x": split_x,
                  "panel_roles": roles, "displacement_budget": DISPLACEMENT_BUDGET,
                  "max_tile_px": 2000, "min_text_px": 15,
                  "mode": "keyframes_only_no_stitch"},
        "segments": segments,
        "coverage": {"kept_keyframes": len(kept),
                     "represented_in_outputs": len(represented),
                     "orphans": orphans,
                     "dropped_duplicate_tiles": dropped_dups},
        "warnings": warnings,
    }
    (ingest / "manifest.json").write_text(json.dumps(manifest, indent=2),
                                          encoding="utf-8")

    n_tiles = sum(len(v) for v in emit_set.values())
    n_dups = sum(dropped_dups.values())
    report = [f"# INGEST REPORT — {video.name}",
              f"mode: keyframes-only (no stitch); {meta['frames']} frames decoded, "
              f"{len(kept)} keyframes kept, {len(segments)} segments",
              f"panel roles: {roles}; tiles emitted: {n_tiles} "
              f"(left {len(emit_set['left'])}, right {len(emit_set['right'])})",
              f"dedup: {n_dups} scroll-back duplicate tiles dropped "
              f"(left {dropped_dups['left']}, right {dropped_dups['right']}) — "
              f"still coverage-represented by raw keyframes",
              f"coverage: {len(represented)} represented, {orphans} orphans"]
    report += [f"WARNING: {w}" for w in warnings]
    (ingest / "INGEST_REPORT.md").write_text("\n".join(report) + "\n",
                                             encoding="utf-8")
    return manifest, orphans, warnings, roles, n_tiles


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("recording", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--split-x", type=int, default=None,
                    help="x pixel dividing left/right panels "
                         "(default: mid-width, the Henna two-panel layout)")
    ap.add_argument("--stride", type=int, default=ANALYSIS_STRIDE,
                    help=f"Pass-1 frame sampling stride (default {ANALYSIS_STRIDE}; "
                         "1 = analyze every frame)")
    args = ap.parse_args()
    if not args.recording.is_file():
        print(f"FAIL: {args.recording} not found")
        return 1

    log(f"pass 1: analyzing {args.recording.name} (stride {args.stride}) ...")
    stats, meta = analyze(args.recording, stride=args.stride)
    log(f"  {meta['frames']} frames, {meta['width']}x{meta['height']} "
        f"@ {meta['fps']:.0f}fps, {len(stats)} sampled")

    kept, boundaries = select_keyframes(stats, meta)
    log(f"  selected {len(kept)} keyframes, {len(boundaries)} segment starts")

    split_x = args.split_x or meta["width"] // 2
    log(f"pass 2: emitting (split_x={split_x}) ...")

    manifest, orphans, warnings, roles, n_tiles = emit(
        args.recording, args.out, kept, boundaries, meta, split_x)
    log(f"  panel roles {roles}; {n_tiles} tiles; "
        f"{sum(len(s['outputs']) for s in manifest['segments'])} total outputs")

    if orphans:
        log(f"FAIL: coverage gate — {orphans} orphan keyframes")
        return 1
    if warnings:
        for w in warnings:
            log(f"WARN: {w}")
        return 2
    log("ok — next: python video_pipeline/tools/label_tabs.py " + str(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
