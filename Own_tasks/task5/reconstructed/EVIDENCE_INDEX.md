# EVIDENCE INDEX — task5 (qa_002, temporal)

Searchable reconstructions (Markdown = index; saved keyframes in `ingest/pages/` are ground truth).

| Tab | Doc | Page | File | Role |
|---|---|---|---|---|
| Doc1 P1-4 | 9789812831415.pdf (Vol 6) | 4 | `doc1_p4_copyright.md` | **DECISIVE** — Vol 6 "Copyright © 1995" |
| Doc2 P8-11 | 9789812816610.pdf (Vol 8) | 8 | `doc2_p8_copyright.md` | **DECISIVE** — Vol 8 "Copyright © 1998" |
| Doc2 P8-11 | 9789812816610.pdf (Vol 8) | 9 | `doc2_p9_preface.md` | **DECISIVE** — Preface: Vol 6 in 1995, Vol 7 in 1996, "frequency of one per year" |

## Decisive comparison (verify against images, never against Markdown)
- Vol 6 copyright year = **1995** [Doc1 Page 4] `<!-- f00329_left -->`
- Vol 8 copyright year = **1998** [Doc2 Page 8] `<!-- f01223_left -->`
- Stated cadence = **one volume per year (1.0 yr/vol)** [Doc2 Page 9] `<!-- f01311_left -->`
- Arithmetic (computed with code): Vol 6→8 = 2 volume steps; 1998−1995 = 3 years; 3/2 = **1.5 yr/vol** > 1.0 → **slower than annual** ⇒ option **D**.

## Why A/B/C are wrong
- A: says "faster than annual (0.67)" — wrong direction; 1.5 > 1.0 is slower, not faster.
- B: uses 1995→1997 — wrong Vol 8 year (Vol 8 © is 1998, not 1997).
- C: uses 1996→1998 — wrong Vol 6 year (1996 is Vol 7's year per the Preface; Vol 6 © is 1995).

## Non-decisive pages (no copyright-year / cadence data — confirmed from frames)
Doc1 P1-3 title/cover; Doc1 P5-8 contents; Doc2 P4-7 blank+title; Doc2 P10 blank, P11+ article contents; Doc2 P12-14 editor/advisory-board.
