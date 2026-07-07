# WORKFLOW: REVIEW_TASK — reviewing an attempter's submission

Role reminder: you are NOT redoing the task; you verify the attempter applied the rules.
But approving bad work is a quality failure, so verification is real, not a skim.
Budget: ~5 minutes. If genuinely unverifiable in that window, reject with a note saying why.

## Pipeline

1. **Orient (1 min)**: read question + AI answer; note attempter's verdict; scan their
   quotes and pages.
2. **Evidence check (2 min)**:
   - Open every cited page; confirm each quote appears **word for word** (minor OCR noise
     tolerated, paraphrase is a reject).
   - Table/figure/formula/layout answers ⇒ verify against the PDF Reference tab.
   - Confirm the pages field lists exactly the quoted pages — no padding, no gaps.
3. **Verdict check (1 min)**: does the quoted evidence actually entail the verdict?
   Run the special-case rules (MC option-only, not-answerable, exact-text, completeness).
   For numeric tasks, recompute the arithmetic with code — never accept stated sums.
4. **Format & note check (30 s)**: `[Page X] "exact text"` format; note present whenever a
   mandatory-note situation applies (NOTES_RULES §4).
5. **Decide**:
   - All four checks pass ⇒ **Approve / Sign off**.
   - Work is close (small format fix, missing note you can add) ⇒ improve & approve if the
     platform allows edits; otherwise reject with the precise fix.
   - Any check fails fundamentally ⇒ **Reject / Needs work** with at least one comment.

## Rejection comment style (mandatory)

One line per issue, names the issue, points to the fix, references pages:
- "Verdict should be Wrong. The evidence on page 12 contradicts the answer."
- "Quote does not appear on page 5. Please re-check the cited page."
- "Please add a note. The answer depends on a value from the table on page 8."
List EVERY issue found — a partial list causes SBQ ping-pong.

## Reviewer's three final questions (answer all before submitting the review)

1. Does the verdict follow from the evidence?
2. Is the evidence quote real, complete, and on the right page?
3. Was a note added if one was needed?
All yes ⇒ Approve. Any no ⇒ Reject with one-line comments.
