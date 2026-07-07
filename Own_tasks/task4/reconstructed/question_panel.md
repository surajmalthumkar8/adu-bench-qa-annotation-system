# Question / Form panel — task4 (qa_006, set_difference, cross-doc, multiple-choice)

> Source: task4.md (pasted task content = authoritative). The AI-generated choice is withheld here so the independent-solver stays un-anchored.

## 📝 Question
In publication data, treating eISBN/e-book and ISSN/series ISSN as unified, which label appears only in *Properties of Single Organic Molecules*, not *Electron Scattering*?

Options:
- **A.** e-book/eISBN appears only with ISBN 1-86094-628-3
- **B.** DOI appears only with ISBN 1-86094-628-3
- **C.** ISSN/series ISSN appears only with ISBN 1-86094-628-3
- **D.** No extra label; both list one ISBN

## Format / Verify
- **Format:** Str
- **Verify:** `choice_exact_match`
- **Tags:** set_difference
- **Cross-doc:** ⚠️ Yes

## Mapping
- *Electron Scattering* = Doc1 (9789812830883.pdf); its ISBN is 981-02-2300-5.
- *Properties of Single Organic Molecules on Crystal Surfaces* = Doc2 (9781860948053.pdf); its ISBN is 1-86094-628-3.
- Publication data lives on each book's copyright page: Doc1 Page 5 and Doc2 Page 5.

## Evidence tabs present (completeness contract)
Doc1 P1-2, Doc1 P3-4, Doc1 P5 / Doc2 P1, Doc2 P2-3, Doc2 P4-5, Doc2 P6-7, PDF.
Only the two copyright pages (Doc1 P5, Doc2 P5) carry publication-data labels; all other front-matter pages are cover/title/half-title/blank/contents (verified from frames).
