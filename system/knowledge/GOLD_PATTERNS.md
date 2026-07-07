# GOLD PATTERNS — distilled from the 16 signed-off tasks in Others_tasks/

These are the patterns that got teammates' work signed off. Extracted, not memorized:
apply the pattern, not the example.

## 1. Evidence Quotes — observed conventions

- Canonical citation: `[Doc1 Page 4] "quoted text"` (space-separated; a few signed-off
  tasks used `[Doc1, Page 3]:` and single quotes and still passed — the canonical form is
  safest; consistency within a submission matters more than the variant).
- One citation block per fact; multiple quotes separated by blank lines.
- Multi-line source text is kept multi-line inside the quote (e.g. author + affiliation on
  two lines) — verbatim beats pretty.
- Quotes are surgical: the sentence(s) or line item(s) that decide the verdict, nothing more.
  Longest observed quote ≈ 3 sentences (a theorem statement that was itself the evidence).
- For every operand of a calculation there is a quote. 3 operands ⇒ 3 quotes from up to
  3 documents (gold examples 3, 15).
- LaTeX/math in evidence is quoted in readable inline form
  (`"Theorem 5.2 ... χ(X) = Σ I(v,a_i)"`), close to source, not re-derived.
- Never an explanation, calculation, or opinion inside this field. Quotes only.

## 2. Evidence Pages Used — observed conventions

- Cross-doc: `Doc1: 4 | Doc2: 4` / `Doc1: 91 | Doc2: 38` / `Doc1: 3 | Doc2: 3 | Doc3: 3`.
- Single doc: bare numbers `37` or `5, 6`.
- STRICTLY minimal — only pages a quote came from. The onboarding transcript is explicit:
  pages 20–22 were read but only 27 & 29 were useful ⇒ only 27, 29 listed.
- Pages field must be consistent with the pages named in the quotes (reviewers cross-check).

## 3. Notes — the house style

Signed-off notes share a recognizable voice. Rules extracted:

- **1–4 sentences of plain prose.** No headers, no bullets (one exception used short
  labeled lines for a multi-step calc — acceptable when arithmetic has ≥3 steps).
- **State the reasoning that connects quotes → verdict**, not a restatement of the verdict.
  All arithmetic lives here (never in quotes): "Fixed-Film delay = 325 − 1 = 324,
  Activated Sludge delay = 465 − 1 = 464. The difference is 464 − 324 = 140."
- Reference docs/pages inline in prose ("on Doc2 page 9", "Doc1 page 5 identifies...").
- For Wrong verdicts, name the precise defect: "Answer is incomplete, it just says
  'u; v; w' but it does not mention which columns & rows are involved" (gold example 10).
- Sometimes opens with the verdict ("This is Correct.") — optional, fine either way.
- Sounds like a person: contractions ok, no filler ("It is worth noting that..."), no
  hedging, no AI-tell phrases. Notes that read as generated get scrutinized.

## 4. Verdict reasoning patterns that got sign-off

- **Independent recomputation**: every numeric answer was recomputed from quoted operands
  (75 = 15/0.2; 140 = 464−324; 6.5 = 12−(4+7)/2; 19 = 10+9; 42 = 99−57 with inclusive dates).
- **Both sides quoted for reconciliation**: to prove two entries denote one entity, both
  renderings are quoted from both docs.
- **Full-list enumeration for coverage/absence claims**: to prove Vols 1 & 2 absent, the
  note establishes the Published list runs Vol 12 → Vol 5, so absence is proven, not assumed.
- **Every component of a multi-part option verified** (consistency triples): one quote per
  component, note walks all three.
- **Wrong for incompleteness**: an answer that is true but does not address every part of
  the question is Wrong (example 10). Completeness is judged against the QUESTION, not
  against truth.
- **Out-of-context number trap (learned task1)**: a number that appears in the evidence is
  only usable if it denotes the exact entity the question asks about. task1 asked for the
  transcendence degree of the function field F; Doc2 printed values 4, 6, ≤2 that looked
  tempting but described a different object (the invariant subfield L). The correct answer
  (3) came from the shared n = 3 variable setting via Doc1's dim = trdeg(F/k) definition,
  not from grabbing the nearest printed integer. Always confirm the quoted value's subject.
- **Derived-quantity / restated-operands trap (learned task6)**: on a comparison/aggregate
  question whose options ask for a DERIVED result (a range, min, max, count, or grouping)
  AND whose distractors all share the same operand set, an answer that just lists the
  operands answers nothing — it neither gives the derived value nor the earliest/latest (or
  which-is-which) assignment, and it fails to disambiguate the options. task6 asked for the
  latest−earliest January start-day range across five PSB volumes with the earliest/latest
  years; the AI "answered" with the bare list "2003; 2005; 2006; 2007; 2008" (the year union
  shared by options A/B/D) ⇒ Wrong; the supported option was D (range 1; earliest day 3 =
  2003/2006/2007, latest day 4 = 2005/2008). Judge the DERIVED quantity the question asked
  for, not whether each listed input is individually supported.

## 5. Meta-observations

- All 16 gold tasks are cross-document; expect cross-doc as the norm.
- The "Notes (Optional)" label is a trap — every signed-off task filled it. The transcript
  says outright: every field is required, including ones marked optional.
- Nobody quotes tab labels; everyone quotes `DocN` + document page number.
- Where the AI answer disagreed with a naive reading, gold annotators trusted the
  **Verify field semantics** (e.g. set_match ⇒ set answer acceptable without option letter).
