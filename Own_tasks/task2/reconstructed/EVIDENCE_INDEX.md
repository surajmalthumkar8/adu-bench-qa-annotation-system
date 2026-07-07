# EVIDENCE INDEX — task2 (qa_022, adu-bench-crossdoc-v2)

Maps each evidence tab (DocN Page Y) to its reconstruction file and the ground-truth
tile images. Decisive values are verified against the images listed here, never
against the Markdown (per INGEST_VIDEO Step 7 / ARCHITECTURE §6 Step 6).

## Evidence tabs (from chrome/tabbar.png — the completeness contract)

| Tab | Document (ISBN) | Reconstruction | Key ground-truth tiles |
|---|---|---|---|
| Doc1 P6 | Dynamic Fracture Mechanics — 9789812773326.pdf | `doc1_p6.md` | pages/f00071_left … f00695_left; probe frame |
| Doc1 P7 | Dynamic Fracture Mechanics — 9789812773326.pdf | `doc1_p7_p8_p9.md` | pages/f00840_left.png |
| Doc1 P8 | Dynamic Fracture Mechanics — 9789812773326.pdf (Contents) | `doc1_p7_p8_p9.md` | pages/f00991_left.png |
| Doc1 P9 | Dynamic Fracture Mechanics — 9789812773326.pdf (Ch.1) | `doc1_p7_p8_p9.md` | pages/f01128_left.png |
| Doc2 P12 | Fracture and Life — 9781848162839.pdf (Contents) | `doc2_p12.md` | pages/f01194_left.png (top) … f01382_left.png (deepest) |
| Doc3 P20 | Dislocation Based Fracture Mechanics — 9789812796363.pdf (Contents) | `doc3_p20.md` | pages/f01490_left.png (top) … f01580_left.png (deepest) |
| PDF | Original PDF page images (reference tab) | (revisit stretch; same content as markdown tabs) | pages/f016xx–f020xx |
| Question panel | Question + AI Answer + Verify line + form | `question_panel.md` | pages/f00320_right, f00443_right, f01216_right, f01400_right |

## Decisive values for THIS question (start-page numbers, verified against tiles)

- **Doc2 (Fracture and Life) — first natural/geological entry on P12:**
  `2.3 Earthquakes 36` <!-- src: pages/f01194_left.png (first entry directly under breadcrumb) -->
  (followed by 2.4 Rock Fracture 41, 2.5 Ice 46, 2.5.1 Glaciers 47, 2.5.2 Icebergs 49)
- **Doc3 (Dislocation Based Fracture Mechanics) — first earth/geological entry on P20:**
  `10.1.1. Crevasses 373` <!-- src: pages/f01490_left.png (first entry after TABLE OF CONTENTS xix) -->
  (followed by 10.1.2 Propagation of Magma Filled Cracks 379, 10.1.3 Dikes 380)
- **Doc1 (Dynamic Fracture Mechanics):** Contents (P8) lists only dynamic/engineering
  chapters (1..9 → pages 1,69,104,147,199,236,273,310,339); **no earth/ice/geological
  entry** → the "mismatch" document per the question.

## Completeness notes carried to the gate

- Doc2 P12 begins at `2.3 Earthquakes 36` (entries 2.1/2.2 and the Chapter 2 title are on
  a page NOT provided as a tab — but on the provided evidence page, 2.3 is the first).
- Doc3 P20 begins mid-chapter at `10.1.1. Crevasses 373`; the `10.1` section header is on
  a prior (non-provided) page. First entry on the provided page = Crevasses 373.
- Both Contents pages have a `[CONTINUES]` at the bottom (recording did not scroll to the
  page end); this does not affect the first-entry values the question requires.
