# WORKFLOW RULES — compulsory execution (no exceptions)

These rules govern HOW the workflows run. They are as binding as the verdict rules.

1. **A pasted task ALWAYS triggers the full DO_TASK workflow.** Every numbered step
   runs, in order, every time. No step is skipped for "simple" tasks — simple-looking
   tasks are where anchoring and format slips happen.
2. **Every agent in the chain is dispatched every task. None may be skipped or inlined:**

   | # | Agent | Role | May be skipped? |
   |---|---|---|---|
   | 1 | `evidence-hunter` | evidence sweep (one per doc on large tasks) | NO |
   | 2 | `independent-solver` | unanchored solve — never sees the AI answer | NO |
   | 3 | `reviewer-simulator` | adversarial correctness gate | NO |
   | 4 | `humanizer` | rewrites the note into the gold corpus voice — always LAST edit to content | NO |
   | 5 | `final-evaluator` | last gate: end-to-end + humanization validation | NO |
   | 6 | `lessons-scribe` | learning agent — writes the LESSONS entry + applies the rule edit, every task | NO |

3. **All subagents run on Opus** (`model: opus` pinned in every `.claude/agents/*.md`
   frontmatter — resolves to Opus 4.8, the strongest subagent model). Never dispatch an
   annotation agent with a smaller model override. The orchestrating main loop runs on
   the session's strongest model.
   **Fallback (mandatory, never skip instead):** if a named agent type is not yet
   registered in the current session (agents load at session start), dispatch a
   `general-purpose` agent with `model: opus` whose prompt says to read and follow the
   corresponding `.claude/agents/<name>.md` definition exactly. The chain runs either
   way — smoke-tested 2026-07-05.
4. **Gate order is fixed**: `tools/validate_submission.py` CLEAN → `reviewer-simulator`
   APPROVE → `humanizer` rewrite → validator re-run on the humanized note (CLEAN) →
   `final-evaluator` SHIP. Only then deliver.
5. **The humanizer is content-final**: nothing edits the note after it except a
   final-evaluator-triggered rework, which must go BACK through the humanizer.
   The humanizer never touches Evidence Quotes (verbatim is sacred). It ALWAYS runs the
   `humanizer` skill (`.claude/skills/humanizer/`) on the note — mandatory, every task —
   so the note is concise, casual, and plain, never AI-sounding, robotic, or "too smart"
   (Suraj standing rule). The final-evaluator confirms the skill ran and rejects a note
   that reads clever/polished.
6. **Any gate failure loops back** to the step that owns the defect (evidence → sweep,
   verdict → solve/adjudicate, format → draft, voice → humanizer), then ALL downstream
   gates re-run. Gates are never "passed on memory" of a previous run.
7. **No delivery without the verification summary** stating truthfully which gates ran
   and what was recomputed. If a gate did not run, the deliverable does not ship.
8. **Continuous learning is part of the workflow, not optional — and it is an AGENT:**
   - Every task ends with the `lessons-scribe` agent (DO_TASK step 11 / INGEST_VIDEO
     step 8): it writes the LESSONS.md entry AND applies the owning rule/knowledge edit
     in the same session. A clean run still gets a short entry; a caught defect gets a
     root-cause + structural-guard edit. The learning loop is no longer a manual memory.
   - Before the first task of a session: `Glob Others_tasks/*.md` and compare against
     the corpus — any file not yet reflected in `NOTE_STYLE_CORPUS.md` /
     `GOLD_PATTERNS.md` gets distilled FIRST (new notes appended verbatim to the
     corpus; new patterns/verify-types/task-tags added to the knowledge files).
   - After any reviewer feedback on our delivered work: lessons-scribe entry + rule edit
     before the next task is attempted.
9. **Incomplete input never proceeds** (DO_TASK step 1 gate): missing evidence tabs or
   unreadable decisive values are asked for by name. Verdicting on partial evidence is
   a workflow violation even if the verdict turns out right.
10. **Visual verification is binding** (`VISUAL_VERIFICATION_RULES.md`): every decisive
    value is read off the image/PDF pixels (not Markdown), confusable glyphs resolved, and
    confirmed by TWO independent sources; any disagreement between the evidence-hunter's
    and independent-solver's reads is a BLOCKING re-read before the verdict. Derived
    quantities (range/min/max/count/grouping) are re-computed with code, and a restated-
    operands answer to a derived-quantity question is Wrong (VERDICT_RULES §4).
