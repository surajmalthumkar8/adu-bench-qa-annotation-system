# NOTES RULES — the Notes field

1. **Always filled.** The "(Optional)" label is cosmetic; the project treats it as required
   (attempter guidelines: "NOT optional. ALWAYS COMPLETE IT"; transcript: every field
   including optional ones must be filled).
2. **1–4 sentences of plain human prose.** Exception: a multi-step calculation may use
   short labeled lines (see GOLD_PATTERNS §3).
3. Content = the bridge from quotes to verdict:
   - all arithmetic, step by step ("15 / 0.2 = 75"),
   - entity-matching logic for reconciliation,
   - full-list reasoning for absence/coverage claims,
   - the precise defect for Wrong verdicts ("incomplete: does not name rows/columns").
4. Mandatory-note situations (reviewer rejects if missing): ambiguous evidence; partially
   correct answer; PDF vs markdown mismatch; answer depends on a table/figure/formula/
   diagram; multiple pages needed; answer format close but not exact; any calculation.
5. Style: sounds like a teammate, not a model. No headers, no "Furthermore/Moreover",
   no rule-of-three flourishes, no hedging ("it seems", "likely"), no restating the task.
   Reference evidence inline as "Doc2 page 9" / "page 5".
6. Never put quotes-only content here and never put reasoning in the quotes field —
   the two fields have disjoint jobs.
7. The note's final form ALWAYS comes from the `humanizer` agent (DO_TASK step 8),
   grounded in `knowledge/NOTE_STYLE_CORPUS.md`, and is validated by the
   `final-evaluator` agent (HUMANIZATION: PASS required). No content edits after the
   humanizer except via loop-back through it.
