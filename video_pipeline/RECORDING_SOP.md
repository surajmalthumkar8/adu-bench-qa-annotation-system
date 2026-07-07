# RECORDING_SOP — How to record a task so the pipeline can succeed

The pipeline can only reconstruct pixels that exist in the mp4. These rules exist
because each one maps to a known failure mode (ROADMAP risk register). Draft status:
finalized in Phase 3 from real-recording experience.

## Hard requirements

0. **Recorder quality settings — the single highest-impact rule in this document.**
   Research finding: one settings change delivers more text legibility than every
   post-processing technique combined. Standard recordings use 4:2:0 chroma
   subsampling (quarter-resolution color) and aggressive compression, which smears
   glyph edges and makes small colored text unreadable. In OBS (or equivalent):
   - Output mode **Advanced** → Recording → rate control **CQP/CRF ≤ 16**
     (or true lossless: x264 `qp=0` — a 2–3 min clip stays manageable);
   - Settings → Advanced → **Color Format I444** (4:4:4), **Full** color range;
   - Container **MKV** (crash-safe; remux to mp4 after if needed);
   - Base (canvas) resolution = Output resolution = native display resolution —
     any scaling mismatch blurs text;
   - 30 fps is enough (the pipeline picks frames by scroll displacement, not rate).
1. **Resolution ≥ 1440p** (2560×1440) if possible; 1080p minimum. Below 1080p width
   the CLI warns and legibility of decisive characters (ISBN digits, table cells) is
   at risk. (R1)
2. **Body text ≥ ~14 px on screen.** Use browser/PDF zoom of 100% or more; if the
   platform renders small, zoom in. When in doubt: if you can read it comfortably,
   Claude can.
3. **Scroll every inner horizontal scrollbar fully to the right** — wide equations and
   tables in the Henna panel hide content behind inner h-scrollbars. If you don't show
   it, it does not exist for the system. (R2)
4. **Visit every evidence tab** listed in the tab bar (`Doc1 …`, `Doc2 …`, `PDF`), and
   scroll each to the bottom of its relevant range. The system reads the tab bar and
   will BLOCK and ask you for any tab the recording never opens.
5. **Include the question + AI answer panel** (with the Format/Verify/Tags line) in the
   recording — the system needs it to identify document roles.

## Strong recommendations

6. **Take your time — 2–3 minutes is better than 60–90 seconds.** Fast scrolling causes
   motion blur and missed content; the dedup stage removes redundancy for free, so a
   slower recording costs nothing downstream. (R6)
7. **Scroll in discrete wheel steps with brief pauses** (~0.5 s) rather than smooth
   drag-scrolling. Each pause gives the pipeline a sharp frame. (R3, R6)
8. **One direction per document: top → bottom.** Avoid scrolling back up mid-document;
   if you need to revisit, finish the pass first, then scroll back (the stitcher
   handles it, but monotonic passes stitch cleanest).
9. **Avoid zooming mid-recording.** If you must zoom (e.g., a small figure), pause on
   it for ~1 s — the zoomed stretch is emitted as separate keyframes.
10. **Keep the mouse out of the text** while scrolling; hover-highlights and tooltips
    occlude content. Park the cursor on the scrollbar or margin. (R7)

## Recorder settings to verify (open questions, Phase 0)

- [ ] Does your recorder burn in a cursor or click-highlight overlay? If togglable,
      turn click-highlights OFF. (R7)
- [ ] Capture region: full task window including the question/answer panel — not just
      the evidence pane.
- [ ] Output: MKV or mp4 (H.264), CQP/CRF ≤ 16, I444 color format, native resolution,
      30 fps (see Hard requirement 0 — these settings matter more than anything the
      pipeline does afterward).

## Quick pre-flight (10 seconds)

Zoom OK → tab bar visible → start recording → question panel → AI answer →
each Doc tab top-to-bottom (drag wide equations right) → PDF tab → stop.
