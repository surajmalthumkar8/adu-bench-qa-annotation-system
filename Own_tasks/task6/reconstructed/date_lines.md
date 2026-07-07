# Date-line evidence — task6 (qa_048, comparison, cross-doc)

> Reconstructed by orchestrator directly from base keyframes (DECISIVE — each
> title page carries the "City, State D-D January YYYY" conference date line;
> image is ground truth). Start day = the FIRST number in the "D-D January" range.
> NOTE: on Doc3 and Doc5 the location and the date sit on SEPARATE lines — quote
> the date line on its own; never stitch location+date into one citation.

| Doc | ISBN file | Title page | Year | Date line (verbatim) | Jan start day |
|---|---|---|---|---|---|
| Doc1 | 9789812776303.pdf | Page 4 | 2003 | `Kauai, Hawaii 3-7 January 2003` (one line) | **3** |
| Doc2 | 9789812702456.pdf | Page 4 | 2005 | `Hawaii, USA 4-8 January 2005` (one line) | **4** |
| Doc3 | 9789812701626.pdf | Page 4 | 2006 | `Maui, Hawaii` / `3-7 January 2006` (two lines) | **3** |
| Doc4 | 9789812772435.pdf | Page 4 | 2007 | `Maui, Hawaii 3-7 January 2007` (one line) | **3** |
| Doc5 | 9789812776136.pdf | Page 5 | 2008 | `Kohala Coast, Hawaii, USA` / `4-8 January 2008` (two lines) | **4** |

<!-- src Doc1 P4: f00135_left.png / f00258_left.png — "Kauai, Hawaii 3-7 January 2003" -->
<!-- src Doc2 P4: f00570_left.png — "Hawaii, USA 4-8 January 2005" -->
<!-- src Doc3 P4: f00570_left.png — "Maui, Hawaii" then "3-7 January 2006" (separate lines) -->
<!-- src Doc4 P4: f00795_left.png — "Maui, Hawaii 3-7 January 2007" -->
<!-- src Doc5 P5: f01194_left.png / f01215_left.png — "Kohala Coast, Hawaii, USA" then "4-8 January 2008"; Doc5 P4 = "This page intentionally left blank" -->

## Decisive computation (verify against images, never Markdown)
- Start days by year: 2003→3, 2005→4, 2006→3, 2007→3, 2008→4.
- Set of start days = {3, 4}. earliest = 3, latest = 4.
- Range = latest − earliest = 4 − 3 = **1**.
- Years with earliest day (3): **2003, 2006, 2007**.
- Years with latest day (4): **2005, 2008**.
- ⇒ Option **D** (Range 1; earliest 3 = 2003/2006/2007; latest 4 = 2005/2008).

## Why the other options fail
- A: "Range 2" is wrong (4−3=1, not 2) and "earliest 2" is the wrong day value (min day is 3, not 2).
- B: "Range 1" is right but it SWAPS the groups — it calls 2005/2008 earliest and 2003/2006/2007 latest; evidence shows 2005/2008 start on day 4 (later), 2003/2006/2007 on day 3 (earlier).
- C: "Range 0 / all five same" is wrong — 2005 & 2008 start on the 4th, the others on the 3rd, so they are not all equal.
