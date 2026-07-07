# VISUAL VERIFICATION RULES — how to LOOK at every image and document

Binding, same weight as VERDICT_RULES. Wrong answers on this project come almost
entirely from *mis-reading a pixel* or *trusting a derived claim without re-deriving it*.
These rules make looking-hard a gate, not a hope. They apply to every screenshot, every
reconstructed tile, and every PDF-reference image.

## 1. Decisive-value protocol (per value, no exceptions)

A **decisive value** is any token the verdict turns on: a digit, year, ISBN, page number,
option letter, name, table cell, set member, date, or the presence/absence of a line.

For EVERY decisive value:
1. **Read it off the actual image pixels** (the keyframe tile or PDF reference), character
   by character — never off reconstructed Markdown alone. Markdown is a searchable index;
   the image is ground truth (this is the standing "images are truth" rule).
2. **Transcribe it verbatim** into the working notes with a `src` pointer to the exact
   tile/frame it was read from, so any gate can re-open that pixel.
3. **Confusable-glyph check.** Explicitly disambiguate the known confusions before trusting
   a value: `3↔8`, `1↔7`, `0↔O`, `5↔6`, `rn↔m`, `l↔1`, comma↔period in numbers, en-dash↔
   hyphen in ranges, `©`-year vs printing-year. State which glyph you confirmed when a
   value is confusable (e.g. "4-8, the 4 is open-top not a 9").
4. **Two-source triangulation (BLOCKING).** Each decisive value must be confirmed by TWO
   independent reads before it can carry a verdict:
   - the evidence-hunter's read AND the independent-solver's read, or
   - two different frames/tiles showing the same value, or
   - the reconstructed text AND the raw keyframe.
   If the two reads DISAGREE on any decisive value ⇒ STOP, re-open the pixels, and resolve
   against the image before proceeding. A verdict may never rest on a single unconfirmed read.

## 2. Look at the WHOLE surface, not the first hit

- **Sweep every provided page/tab** before concluding — including the ones that look like
  filler (blank pages, half-titles, covers). Absence is only proven after an exhaustive
  sweep (VERDICT_RULES: no Wrong-for-unsupported on a partial look).
- **Scroll-boundary check.** If a decisive line could sit at a tile's top/bottom edge, find
  the tile where it appears WHOLE. Never read a value that is clipped at a tile edge —
  open the overlapping neighbour tile (or the raw keyframe) where it is complete.
- **Separate-line integrity.** Text on two physical lines (e.g. a city line and a date
  line) stays two quotes — never stitch across a line break to form one citation
  (standing quote-integrity rule; the single most common historical send-back).
- **Layout wins.** For tables, figures, formulas, captions, multi-column, or any place the
  Markdown looks broken, the PDF Reference image is the source of truth (VERDICT_RULES §4).

## 3. Re-derive every derived quantity — never read it off the answer

- Any range, sum, mean, count, difference, gap, set size, or membership is COMPUTED with
  code from the pixel-verified operands (never mental math, never trusting the AI's math).
- **Derived-quantity trap (task6).** When a question asks for a DERIVED result (a range /
  min / max / count / grouping) and the distractor options share the same underlying operand
  set, an answer that merely restates the operands (e.g. "lists all five years") is a
  NON-ANSWER — it supplies neither the derived value nor the required assignment. Judge the
  derived quantity the question asked for, not whether the listed inputs are individually
  supported. A true-but-non-responsive list is **Wrong** (see GOLD_PATTERNS).

## 4. Attestation (what the gates check)

Before a submission ships, the working record must show, for every decisive value:
`value — src:<frame/tile> — glyph-checked — confirmed by <2 sources>`.
- The **reviewer-simulator** rejects any decisive value lacking a pixel `src` or a second
  confirming source, and any derived quantity it cannot re-compute from quoted operands.
- The **final-evaluator** re-computes every derived quantity and confirms each decisive
  value is pixel-anchored, not Markdown-anchored, before SHIP.
- Unreadable decisive value after these steps ⇒ ask Suraj for a closer capture by name;
  never infer, never average a guess.
