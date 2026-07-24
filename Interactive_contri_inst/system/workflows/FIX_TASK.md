# WORKFLOW: FIX_TASK — reviewer feedback / flag / rejection on an SxS task

Trigger: Suraj pastes reviewer feedback, a low-effort/repetition flag, or a
rejection for a delivered SxS task.

1. **Reconstruct** — load the task's state file + LESSONS entry + the delivered
   turns/picks. Identify exactly what the reviewer objected to (turn, pick, voice,
   repetition, PII, padding).
2. **Root-cause to an owning step** — which DO_TASK step let it through, and which
   rule/knowledge file should have caught it. "Reviewer was wrong" requires quoted
   evidence from the instructions before it can be the conclusion.
3. **Fix forward** — if the platform allows amending: run the owning DO_TASK steps
   fresh (full gates) and deliver the corrected piece. If not, the fix is purely
   structural.
4. **Structural edit (mandatory)** — dispatch sxs-lessons-scribe with the feedback +
   root cause. It writes the LESSONS entry AND applies the rule/knowledge/validator
   edit in the same session. If the miss was voice, the offending text and the
   corrected text both go into LESSONS; if a new signed-off example exists, distill
   it into HUMAN_VOICE_CORPUS + GOLD_PATTERNS.
5. **Regression check** — confirm the edited rule would have caught the miss
   (re-run the validator/reviewer-simulator mentally against the old deliverable).
   Only then is the next task allowed.
