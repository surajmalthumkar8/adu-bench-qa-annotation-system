# VERDICT RULES — binding decision procedure

Golden rule (final tiebreaker for everything):
**"Can I point to exact document evidence that proves this answer is correct?"**
Yes ⇒ Correct. No ⇒ Wrong. There is no third option.

## Decision tree

1. **Parse the question into atomic requirements** (target entity, operation, exclusions,
   exactness demands, answer form). If the answer fails ANY requirement ⇒ Wrong.
2. **Locate evidence for every requirement.** Missing/insufficient evidence ⇒ Wrong
   (never Correct-by-plausibility, never outside knowledge).
3. **Apply the Verify-field semantics** (see TASK_ANATOMY §1) when judging closeness:
   - `casefold_exact_match`: case differences OK; missing/extra words NOT OK.
   - `numeric_tolerance`: recompute; trivial rounding OK; wrong value NOT OK.
   - `choice_exact_match`: only the selected option matters.
   - `set_match_casefold`: all members present, no extras; order/case free; set-form
     answers acceptable even when options are lettered.
4. **Special cases** (override intuition):
   - Multiple choice: Wrong if the option is unsupported, even if the explanation contains
     correct information.
   - "Not answerable" answer: Correct ONLY after exhaustively confirming all evidence tabs
     + PDF Reference are silent. If evidence contains the answer ⇒ Wrong.
   - Exact title / exact text / referenced question: the FULL text must be present in the
     answer. Truncation ⇒ Wrong.
   - Partial answers: complete-but-true-so-far ⇒ still Wrong if the question asked for more
     (completeness is judged against the question).
   - **Derived-quantity questions** (range / min / max / count / difference / grouping):
     the answer must supply the DERIVED value and any required assignment. An answer that
     merely restates the operand set — especially when the distractor options all share
     that same set — is a non-answer and is **Wrong**, even though each listed operand is
     individually supported (task6: "list all five years" for a range question ⇒ Wrong;
     the supported option was D). Judge what was DERIVED, not whether the inputs exist.
   - Layout-dependent answers (tables, figures, formulas, captions): the PDF Reference tab
     is the final source of truth. Never decide from broken markdown alone.
5. **Anti-anchoring requirement**: derive your own answer from the evidence BEFORE
   comparing with the AI answer. If your independent answer differs, resolve the conflict
   by re-reading evidence — not by deferring to either answer.

## Prohibitions

- No outside knowledge, ever — not even to "sanity check" a fact.
- No marking Wrong just because evidence wasn't on the first page you checked — you must
  check every evidence tab and the PDF Reference before a Wrong-for-unsupported verdict.
- No verdict before all evidence tabs are reviewed (cross-doc tasks especially).
- Never trust the AI's arithmetic, list membership claims, or date math — recompute.
