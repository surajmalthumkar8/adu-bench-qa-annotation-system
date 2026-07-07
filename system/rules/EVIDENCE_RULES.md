# EVIDENCE RULES — quotes and pages fields

## Evidence Quotes field

1. Format per citation: `[DocX Page Y] "exact evidence text"`.
   Single-doc tasks may use `[Page Y] "..."` (match project examples if shown in-task).
2. **Verbatim only.** Copy-paste from the evidence. No paraphrase, no explanation, no
   arithmetic, no commentary. Minor OCR artifacts from the source are fine to keep.
3. **Complete sentences/entries — never truncate.** Do not use `...` to shorten a quote
   the way a lazy annotator would (called out in the onboarding transcript). If the
   evidence line is long, quote it whole.
4. One quote per decisive fact; separate multiple citations with a blank line.
5. For a Correct verdict: quote the text that CONFIRMS the answer (every operand if it's
   a computation). For a Wrong verdict: quote the text that CONTRADICTS the answer, or
   the closest relevant evidence proving it unsupported.
6. Don't paste huge blocks when one sentence decides it; don't quote pages you don't cite.
7. Document labels: use `DocN` + the document's own page number (as shown in the evidence
   section headers, e.g. "Doc1: 9789812706812.pdf — Page 4"). **Never cite evidence-panel
   tab names** (tabs like "Doc1 P5-6 / Doc2 P1" are groupings, not documents).
8. Broken markdown ⇒ quote from the PDF Reference and put the resource name in the
   bracket: `[<pdf-name> Page Y] "..."` — only in that case.

## Evidence Pages Used field

1. Cross-doc format: `Doc1: 5, 6 | Doc2: 3`. Single-doc: `37` or `5, 6` or `12, 14, 15`.
2. **Minimal set**: only pages a cited quote lives on. Pages you merely read do not belong.
3. Must be exactly consistent with the pages named inside Evidence Quotes — reviewers
   cross-check this in seconds.

## Consistency invariants (machine-checkable — run tools/validate_submission.py)

- Every `[DocX Page Y]` in quotes appears in the pages field, and vice versa.
- Quotes field contains at least one citation; notes field is non-empty.
- No explanation-words heuristics tripped in quotes field (e.g. leading "The answer...",
  "This shows...").
