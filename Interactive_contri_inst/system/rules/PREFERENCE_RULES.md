# PREFERENCE RULES — how A vs B is decided (binding)

Applied by sxs-preference-judge and re-checked inline by the orchestrator. Research
grounding: format-bias study (arxiv 2409.11704), Anthropic sycophancy study (arxiv
2310.13548), length-bias work (arxiv 2407.01085, ACL 2025.findings-naacl.169) —
see `../learning/RESEARCH_BRIEF.md`.

## Decision order (strict — earlier beats later)

1. **Factual/technical correctness.** Verify every checkable claim and EVERY line of
   code in both responses (run/lint code mentally char-by-char; task6's stray `}` is
   the canonical example). A defect the other response lacks is usually decisive.
   Numeric or derived claims get re-computed with code, never mental math.
2. **Instruction & constraint adherence.** Checklist every explicit constraint from
   the CURRENT turn AND every constraint the user set in EARLIER turns (tone, format,
   scope, "don't say gotta", "keep Sunday free"). A violated constraint outweighs any
   amount of polish.
3. **Goal advancement.** Which response actually moves the user's real goal forward —
   answers what was asked, at the right depth, without dodging or bloating?
4. **Sycophancy check.** If the user's premise is wrong, the response that (kindly)
   corrects it beats the one that flatters or agrees. Never reward agreement per se.
5. **Safety/harm.** Anything unsafe, fabricated-confident, or privacy-violating loses.
6. **Clarity and organization** — only after 1–5 tie.
7. **Concision.** Prefer the tighter response when content is equal.

## Bias guards (mandatory neutralizations before judging)

- **Length-neutralize:** longer wins ONLY for added correct + requested content.
  "More detailed" is never a reason by itself.
- **Format-neutralize:** mentally strip bold, lists, emojis, tables before comparing
  substance. Human raters measurably over-reward these; we don't.
- **Position-neutralize:** A-vs-B slot is random. If you notice a pull toward the
  first-read response, re-read in the other order.
- **Confidence-neutralize:** assertive tone ≠ correct. Verify.
- **Shared-defect neutralize:** before crediting any flagged defect (from an auditor
  or your own read) as a differential, confirm the OTHER response does NOT carry it. A
  defect both responses share is a WASH — it decides nothing. A blind auditor sees only
  its assigned response, so a genuine flag there can still be non-differential; the
  judge must cross-check the counterpart before the flag earns weight (task 977: the
  B-audit's car-detailing price flag was real, but A carried the same price floor, so
  it was discarded). Surface this in the BIAS CHECK output.
- **Variance check (cross-task):** if our picks are streaking one side (A,A,A,...)
  or our reasons are converging on a template, flag it — spam filters target
  low-variance patterns. The pick itself never changes for this; the WORDING of
  reasons must not template.

## Near-ties (common — corpus pairs are often ~90% identical)

Pick the one with any real differential (a constraint honored more exactly, a
fresher/more concrete fact, tighter wording, a small defect avoided) and name that
differential as the reason. Record NEAR-TIE in the internal record. Never flip a
near-tie for length/format reasons.

## The reason (optional platform field)

One or two short sentences, first person allowed, casual, citing the SPECIFIC
content differential — never "better formatted", "more detailed", "more
comprehensive", and never rubric-speak ("instruction following", "accuracy").
Corpus-plausible examples of shape: "B repeated the same point twice, A got to the
fix faster." / "A kept Sunday free like I asked." Reason wording must vary task to
task (no template).

## Evidence discipline

The judge's verdict must cite the exact lines/claims that decided it (quote or
pinpoint). "A felt better" is not a verdict. Auditor findings that conflict with
the judge's read ⇒ BLOCKING re-read by the orchestrator before the pick stands.
