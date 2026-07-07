# Question / Form panel — task6 (qa_048, comparison, cross-doc, multiple-choice)

> Source: task6 card (pasted content = authoritative). AI-chosen answer withheld
> here so the independent-solver stays un-anchored.

## 📝 Question
For Pacific Symposium on Biocomputing 2003/2005/2006/2007/2008 date lines, what is
the latest-minus-earliest January start-day range, with earliest/latest years?

Options:
- **A.** Range 2; earliest 2 (2003/2006/2007); latest 4 (2005/2008)
- **B.** Range 1; earliest 3 (2005/2008); latest 4 (2003/2006/2007)
- **C.** Range 0; earliest 3 (all five); latest 3 (all five)
- **D.** Range 1; earliest 3 (2003/2006/2007); latest 4 (2005/2008)

## Format / Verify
- **Format:** Str
- **Verify:** `set_match_casefold`
- **Tags:** comparison
- **Cross-doc:** ⚠️ Yes

## Mapping (year ⇔ document ⇔ decisive page)
- Doc1 = 9789812776303.pdf = PSB **2003** — date line on Doc1 Page 4.
- Doc2 = 9789812702456.pdf = PSB **2005** — date line on Doc2 Page 4.
- Doc3 = 9789812701626.pdf = PSB **2006** — date line on Doc3 Page 4.
- Doc4 = 9789812772435.pdf = PSB **2007** — date line on Doc4 Page 4.
- Doc5 = 9789812776136.pdf = PSB **2008** — date line on Doc5 Page 5 (P4 is blank).

## Evidence tabs present (completeness contract — all 7 confirmed in frames)
Doc1 P1-4 · Doc1 P5-6 / Doc2 P4 / Doc3 P4 · Doc4 P1-4 · Doc4 P5-6 / Doc5 P1-2 ·
Doc5 P3-6 · Doc5 P7 · PDF.
Decisive pages: Doc1 P4, Doc2 P4, Doc3 P4, Doc4 P4, Doc5 P5 (the January date lines).
