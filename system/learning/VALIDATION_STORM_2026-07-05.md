# STORM Validation Report — ADU-Bench Annotation System

> Multi-perspective validation of the built system against the full local corpus (all
> guideline docs, onboarding materials, transcript, and 16 signed-off tasks), plus the
> redesign for the new primary operating mode: **the user pastes task content +
> screenshots, and Claude performs the task end-to-end, first-time-right.**
> Corpus is local by design — the project forbids outside knowledge, so web retrieval
> was deliberately not used. Citations reference repo files.

**Perspectives covered:** reviewer/grader · gold-example falsification · paste-driven
operating mode · first-time-right failure modes · architecture & models

## 1 · Reviewer/grader lens — does the system encode the real approval bar?

Q: Does every reject trigger in the reviewer guidelines [reviwer_rile_guidelines.pdf]
have a countermeasure in the pipeline?
A: Yes — mapped one-to-one: wrong verdict → independent-solver + adjudication; missing/
paraphrased quote → EVIDENCE_RULES §2 + reviewer-simulator step 2; wrong/padded pages →
validator consistency check (tested, catches padding); missing note → NOTES_RULES §1 +
validator; broken format → validator CITE_RE. The reviewer's three final questions are
the reviewer-simulator's output contract [.claude/agents/reviewer-simulator.md].

Q: Is the 5-minute verifiability requirement enforced, not just mentioned?
A: Yes — quotes must be surgical (EVIDENCE_RULES §6), notes ≤4 sentences with explicit
arithmetic (NOTES_RULES §2–3), and the simulator runs the same timed script.

## 2 · Gold-example falsification — would the rules wrongly reject any signed-off task?

Method: replayed all 16 tasks [Others_tasks/] against the rules; recomputed every
numeric task with code; fed the four real citation-format variants to the validator.

- **Arithmetic**: 7/7 numeric tasks recompute exactly (42, 75, 140, 17, 19, 6.5, 6888)
  using the system's methods (inclusive dates = end−start+1, code not mental math). ✔
- **Validator vs gold formats**: `[Doc1 Page 4] "…"`, `[Doc2, Page 9] "…"`,
  `[Doc1 Page 374] '…'` (single quotes), `[Doc1, Page 3]: "…"` — all pass. ✔
- **Note lengths**: all gold notes fall within the 1–4 sentence rule (one labeled-line
  calc exception, already documented in GOLD_PATTERNS §3). ✔
- **No gold example violates any rule in system/rules/.** No false-reject found. ✔

## 3 · Operating-mode lens — the system was built for the wrong entry point

Finding (the big one): ATTEMPT_TASK.md assumes Claude navigates the task in a browser
context. The actual production mode is: **Suraj pastes the task text and screenshots
into chat; Claude produces the complete submission** (verdict to click, quotes, pages,
note — ready to copy-paste). Platform actions (claiming, Attempt URL, submit mirroring)
remain human-side.

Consequences implemented:
- New primary workflow `system/workflows/DO_TASK.md` with an **input-completeness gate**:
  a Wrong-for-unsupported verdict is only legal after a full evidence sweep
  [VERDICT_RULES prohibition #2], so if the paste omits evidence tabs the system must
  ask for them rather than guess — this is the single biggest first-time-right protection
  in paste mode.
- New `system/templates/DELIVERABLE_TEMPLATE.md`: the exact response shape returned to
  the user (what to select + per-field paste blocks + a confidence/verification line).
- Screenshot protocol in DO_TASK: decisive values (ISBNs, years, table cells, option
  letters) transcribed character-by-character from images; unreadable decisive value ⇒
  ask for a closer screenshot, never guess.

## 4 · First-time-right failure modes — ranked, with countermeasures

1. **Incomplete pasted evidence** → input-completeness gate (DO_TASK step 1). New risk
   unique to paste mode; highest severity because it silently flips verdicts.
2. **Anchoring on the AI answer** → unchanged structural fix: independent-solver never
   sees it [ARCHITECTURE §5].
3. **Arithmetic slips** → all math in python; verified against 7 gold tasks.
4. **Screenshot misreading** → transcription protocol + cross-check text↔image; PDF
   image is final for layout [attempter guidelines §07].
5. **Format drift** → validator gate remains mandatory before delivery.

## 5 · Architecture & models

- User requirement: strongest models everywhere. Main loop runs **Claude Fable 5**
  (above Opus-class). All three subagents now pin `model: opus` in frontmatter —
  Opus 4.8 is the strongest model selectable for subagents in this setup, satisfying
  "at least Opus 4.8 for all agents". No agent runs on a smaller model.
- Three-agent design re-validated for paste mode: evidence-hunter (parallel sweep of
  pasted tabs), independent-solver (anchoring firewall), reviewer-simulator (adversarial
  gate). No new agent needed — intake parsing is orchestrator work.
- ATTEMPT_TASK.md retained for direct-platform sessions; CLAUDE.md now routes pasted
  tasks to DO_TASK first.

## Gaps / uncertainties

- Verify-type coverage: only 4 verify functions observed in gold data; new ones (e.g.
  date match, regex) must be added to TASK_ANATOMY §1 on first sighting (LESSONS loop).
- Single-doc tasks: all 16 gold examples are cross-doc; single-doc citation style
  (`[Page X]`) is documented from guidelines but unobserved in gold data.
- Screenshot fidelity depends on what the user captures; the completeness gate mitigates
  but cannot eliminate missing-context risk.

## References
[1] ADU_Bench_Attempter_guidelines.md · [2] reviwer_rile_guidelines.pdf ·
[3] onboarding/transcript_onboarding_ADUB_Project.md · [4] Others_tasks/1–16.md ·
[5] system/rules/* · [6] system/knowledge/* · [7] tools/validate_submission.py test runs
(this session) · [8] onboarding/quick_onboarding_guide_organized.pdf
