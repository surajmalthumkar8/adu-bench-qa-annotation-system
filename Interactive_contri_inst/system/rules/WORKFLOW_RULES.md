# WORKFLOW RULES — SxS Interactive (binding)

1. **The workflow is COMPULSORY.** Any pasted SxS task content ⇒ run
   `../workflows/DO_TASK.md`, every step, in order, every paste. No preamble, no
   shortcuts, no "this pair is obviously A".

2. **All agents dispatch every time, per mode.**
   - MODE START (opening prompt): sxs-turn-writer → sxs-humanizer →
     sxs-reviewer-simulator → sxs-final-evaluator → sxs-lessons-scribe.
   - MODE COMPARE (A/B pasted): sxs-response-auditor ×2 (blind, parallel) →
     sxs-preference-judge → sxs-turn-writer → sxs-humanizer →
     sxs-reviewer-simulator → sxs-final-evaluator → sxs-lessons-scribe.
   - MODE END (turn ≥3, conversation complete): the END recommendation still passes
     reviewer-simulator + final-evaluator + lessons-scribe.
   No skipping, no inlining an agent's job, no matter how simple the paste looks.

3. **Models are pinned.** Orchestrator (main loop) runs on the strongest available
   model (Fable 5). ALL `sxs-*` subagents are pinned `model: opus` (= Opus 4.8) in
   `.claude/agents/*`. Never downgrade any agent.

4. **Blind means blind.** Each sxs-response-auditor sees the conversation history +
   ONE response only. The prompt never mentions the other response, any comparison,
   or any leaning. The turn-writer sees the history + the CHOSEN response only —
   never the loser, never the judge's deliberation (anti-anchoring both directions).

5. **Pick before pen.** The preference is settled (judge + inline adjudication)
   BEFORE the follow-up turn is drafted. Never bend a pick to fit a drafted turn.

6. **Gate chain before delivering (first-time-right is the contract):**
   validator CLEAN → reviewer-simulator APPROVE → humanizer applied → validator
   CLEAN again → final-evaluator SHIP (incl. HUMANIZATION: PASS). Any FAIL loops
   back to the owning step, then the chain re-runs from there.

7. **State is written every paste.** The task state record (turn number, persona,
   constraints, picks so far) is updated per `../templates/STATE_TEMPLATE.md` before
   the deliverable goes out. A follow-up drafted against stale state is a defect.

8. **Incomplete pastes block.** A response that is blank, visibly truncated, or
   missing its pair ⇒ ask Suraj (mention Resample ↺ if a panel failed to load) —
   never judge a partial pair.

9. **Every task ends with sxs-lessons-scribe** (clean runs included): LESSONS entry
   + the owning rule/knowledge edit + PROMPT_LOG update, in the same session.

10. **Reviewer feedback / flags** ⇒ `../workflows/FIX_TASK.md` + LESSONS entry
    (root cause, owning step, rule edit) BEFORE the next task. No miss repeats.

## FAST MODE (standing instruction from Suraj, 2026-07-24 — the default)

Speed is part of the contract: Suraj is live on the platform waiting. Same rigor,
fewer round-trips. MODE COMPARE runs as:

1. **ONE combined `sxs-preference-judge` dispatch (Opus)** doing audit+judgment in a
   single pass: it receives history + BOTH responses, runs both blind-audit
   checklists internally (constraints, claims/code char-by-char, flaws), then
   applies the decision order + ALL bias guards (incl. shared-defect neutralize)
   and returns PICK + quoted differentials + draft reason + draft next turn
   direction. The two-blind-auditors stage is folded in, not skipped in substance.
2. **ONE combined `sxs-humanizer` dispatch** for turn + reason (unchanged).
3. Orchestrator: verify decisive quotes against the paste, write record, run
   validator, self-run the reviewer checklist inline (turn count, anchor, tells,
   PII, shape variety). Separate reviewer-simulator + final-evaluator dispatches
   are RESERVED for: first task of a session, any near-miss/flag, any code-bearing
   response, or when the pick is not clearly defensible. Otherwise inline.
4. Deliver. lessons-scribe runs ONCE per task at task end (background), not per paste.

Full-chain mode (all seven dispatches) remains mandatory for FIX_TASK reruns and
whenever a gate finding or reviewer feedback occurred in the previous 3 tasks' turns.
