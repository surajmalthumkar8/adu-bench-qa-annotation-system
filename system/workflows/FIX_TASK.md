# WORKFLOW: FIX_TASK — handling a send-back (Needs work / SBQ)

SBQs are time-sensitive (top of the priority order) and repeat SBQs on one task trigger
standing review. The goal is a single-cycle fix.

## Pipeline

1. **Locate**: Task History / notifications on Henna → open the task via the
   **Attempt URL you pasted**, NOT the original Task Variables link (fix-flow only).
2. **Ingest feedback completely**: open the Feather comments panel; transcribe every
   issue into a checklist. Do not start fixing until the list is complete — fixing only
   the obvious issue is the classic repeat-SBQ cause.
3. **Re-read the task instructions** end to end. SBQs usually mean an instruction was
   missed; find WHICH rule was violated and log it (step 6).
4. **Fix every item**: `Make edits` in Feather → rerun the relevant ATTEMPT_TASK steps for
   each issue (evidence issue ⇒ steps 1–2; verdict issue ⇒ steps 3–4; format/note ⇒ 5–6, 8).
   Then rerun the full validation + reviewer simulation (steps 6–7) on the corrected
   submission — a fix must clear the SAME bar as a fresh attempt, plus the specific
   feedback items.
5. **Return**: `Mark as fixed` in Feather; mirror any required platform action; resubmit
   promptly.
6. **Learn (mandatory)**: append an entry to `system/learning/LESSONS.md`:
   - task id, reviewer's words (verbatim), root cause, which rule/knowledge file was
     wrong or missing, and the edit made to it.
   A reviewer correction that doesn't change the system is a wasted correction.

## If you believe the SBQ is incorrect

Do not silently comply or ignore: fix what is genuinely wrong, and raise the disputed
point with the project lead per the escalation path (getting_help). Never argue in the
task fields.
