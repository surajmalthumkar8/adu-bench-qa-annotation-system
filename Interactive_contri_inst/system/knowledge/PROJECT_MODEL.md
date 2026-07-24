# PROJECT MODEL — Interactive Preference Collection (SxS Response)

What this project IS, mechanically, so every agent shares the same mental model.
Source of truth: `Interactive_contri_inst/Interactive Contributor Instructions.md` +
the six reference transcripts in `Interactive_contri_inst/reference_tasks/`.

## The product being built

The client ("MAI models" beta test) is collecting **human preference data** for model
training. Each task produces one multi-turn conversation where a real user:
1. types an authentic real-world prompt,
2. receives TWO responses (A and B) from different model configurations,
3. reads both fully, selects the preferred one (optionally noting why),
4. continues the conversation from the chosen response, naturally, for
   **3–5 user turns total** (initial prompt = Turn 1).

The paid deliverable is therefore two things at once:
- **preference signal** (which response won, per comparison), and
- **an authentic conversation trace** (prompts + follow-ups that look like real
  day-to-day AI usage).

Both halves are graded. A perfect pick inside a fake-looking conversation still fails.

## Task flow on the platform (from the instructions)

| Step | Action |
|---|---|
| 1 | Enter a prompt — something you would naturally send an AI assistant |
| 2 | Platform generates two responses (A, B) from different model configs |
| 3 | Read BOTH in full → select the preferred one; optional note why |
| 4 | Continue from the chosen response; keep chatting naturally, up to 5 user turns |

From the reference transcripts: an A/B pair can appear at **every** user turn, not
just the first. The transcript shows the chosen response inline for intermediate
turns and both candidates at the final comparison point ("Conversation continues
from here" marks the continued branch). Treat EVERY pasted A/B pair as a full
comparison to be judged.

## Hard constraints (binding)

- **Turns: minimum 3, maximum 5 user turns.** Initial prompt counts as Turn 1, so at
  least 2 follow-ups after the first comparison. Stop when the conversation feels
  complete — never pad to reach 5.
- **Authenticity is everything** (the instructions' own emphasis): everyday use
  cases — writing help, coding questions, summarizing, brainstorming, explaining
  concepts. Reusing scrubbed prompts from past ChatGPT/Gemini/Claude/Copilot history
  is explicitly encouraged.
- **Flag risks named by the client:** intentionally minimal/trivial prompts,
  repetitive prompts across tasks, artificially difficult or trick prompts, padded
  or filler turns, sensitive/confidential/PII content. "You will be flagged for low
  effort/repetitive tasks."
- **Failed response loads:** never skip/refresh — use the Resample (↺) button on the
  affected panel; if it persists, unclaim and reclaim. (Suraj's side; mention only
  when a pasted response is blank/truncated.)

## Division of labor

Suraj pastes task content (the two responses, or a request to start a task).
Claude runs the compulsory pipeline (`../workflows/DO_TASK.md`) and returns a
paste-ready deliverable: **PICK (A or B) + optional short reason + the next user
message to type** (or the decision to end at turn ≥3). Platform clicks — claiming,
selecting, typing, resampling, submitting — are Suraj's side.

## Session state matters

Unlike ADU-Bench (one-shot verdicts), this project is **stateful across pastes**:
one task = one conversation spanning several pastes. The orchestrator maintains a
state record per task (turn number, persona, topic, constraints already introduced,
what the chosen responses said) — `../templates/STATE_TEMPLATE.md` — so every
follow-up stays coherent with everything said before.
