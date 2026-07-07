# TASK ANATOMY — what every ADU-Bench task contains and what it tells you

## 1. Task fields (right panel)

- **Question** — often long, multi-clause, deliberately convoluted ("Reconciling X with Y,
  which exact Z aligns with...?"). Parse it into atomic requirements before doing anything.
- **Answer** — the AI output under verification. May be a string, number, option letter,
  or a set of items.
- **Format** — `Str` | `Int` | `Float`. Tells you the expected answer shape.
- **Verify** — the *grading function* the benchmark will apply. This is a first-class signal
  for how strict to be:

| Verify value | Meaning for your verdict |
|---|---|
| `casefold_exact_match` | Answer must match evidence text exactly up to letter case. Word order, punctuation, and completeness matter. |
| `choice_exact_match` | Multiple choice: the chosen option must be the right one. Explanations are irrelevant; the OPTION decides. |
| `numeric_tolerance` | Number must be right (small rounding tolerance). Recompute it yourself — never trust the AI's arithmetic. |
| `set_match_casefold` | Answer is a set; all required members present, no extras, order irrelevant. An answer listing set members can be Correct even when the question shows lettered options (seen in gold example 14). |

- **Tags** — the task-type taxonomy (see §2).
- **Cross-doc flag** — if Yes, evidence spans documents; expect the answer to require ≥2 docs.

## 2. Task-type taxonomy (from tags in signed-off tasks)

Each type maps to a verification strategy in `system/workflows/ATTEMPT_TASK.md`.

| Tag | What it asks | Core verification move |
|---|---|---|
| `reconciliation` | Match the same entity across documents despite formatting drift (e.g. "Wai-Kai Chen / University of Illinois at Chicago" vs "W K Chen / University of Illinois, Chicago") | Find BOTH renderings, quote both, confirm they denote the same entity and the answer reproduces the target rendering exactly |
| `comparison` | Compare two values/labels/years across docs (difference, gap, which is higher) | Extract each operand with a quote, compute the comparison yourself |
| `aggregation` | Combine ≥2 numbers (sum, mean, subtotal) | Extract every operand with a quote; recompute; watch for "explicit/headline counts only" exclusion clauses |
| `temporal` | Years, dates, century relations, earlier/later | Extract each date; compute relation; remember inclusive-date counting when specified |
| `counterfactual` | "If X had lasted as long as Y..." hypothetical arithmetic | Compute ACTUAL from evidence, compute COUNTERFACTUAL per the question's rule, then the delta. Inclusive date ranges: end − start + 1 |
| `coverage` | Which item is present in one list but absent from another | Enumerate BOTH lists fully from evidence before judging absence |
| `consistency` | Match a triple/pairing of terms to their sources | Verify EVERY component of the pairing; one wrong component ⇒ Wrong |
| `reference_chain` | Follow a pointer from one doc into another (figure → contents locator → page) | Walk each hop of the chain with a quote per hop |

## 3. Question-language traps (observed)

- **Exclusion clauses**: "excluding e-books/ISSN/set IDs", "using only explicit headline
  counts", "excluding the study with no stated count" — these change which operands are legal.
- **Exact-text demands**: "exact title", "referenced question", "formal label" — the FULL
  text must appear in the answer; a truncated answer is Wrong.
- **Inclusive dates**: "using inclusive dates" ⇒ duration = end − start + 1.
- **"Not answerable" claims**: Correct only if you exhaustively confirmed the evidence is
  silent; if the evidence contains the answer, Wrong.
- **Sampled subsets**: "Which sampled Vol. 1/2/7/9/12 titles..." — the universe is the
  sample listed in the question, not everything in the docs.

## 4. Where evidence hides

- Copyright pages (year, ISBN, publisher) are usually **page 5** of front matter (varies).
- Series lists ("Published / Forthcoming") near the front of each volume.
- Tables of contents give section numbers + start pages (used in delay/locator questions).
- Figure captions carry the solid/dotted-line semantics referenced by questions.
- The SAME physical page can appear in multiple evidence tabs; cite the document page number.
