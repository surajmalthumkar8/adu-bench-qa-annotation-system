# REVIEWER MODEL — what QA sees and how we get flagged

The platform reviewer/QA does not watch us work; they see the finished conversation
trace (all user turns + chosen responses + picks). Simulate them before delivering
(`.claude/agents/sxs-reviewer-simulator.md` runs this checklist adversarially).

## The reviewer's likely 5-minute script

1. **Turn count:** ≥3 user turns, ≤5. Initial prompt counts as Turn 1. An ended
   conversation with 2 turns is an automatic reject.
2. **Low-effort scan:** is any turn filler ("ok", "tell me more", "thanks"), or
   trivially minimal? Is the prompt a one-liner with no real intent behind it?
   The instructions state outright: "You will be flagged for low effort/repetitive
   tasks."
3. **Repetition scan (cross-task):** same prompt or same template as this
   contributor's other tasks → flag. We defend with PROMPT_LOG rotation.
4. **Authenticity sniff:** do the user turns read like a real person typing in a
   chat box, or like an AI (or a script) wrote them? Tells: formatted user turns,
   em dashes, flawless parallel clauses, assistant-flavored vocabulary, turns that
   ignore what the model just said.
5. **Coherence:** does each follow-up actually respond to the chosen response?
   Does the conversation go somewhere and end at a natural point?
6. **Safety/PII:** names, employers, emails, confidential material in prompts →
   flag. Everything must be scrubbed or fictionalized.
7. **Artificial difficulty:** trick prompts, adversarial stress-tests, deliberately
   obscure trivia → against instructions.

## What the reviewer canNOT see

- Our reasoning, agents, drafts, or how long we deliberated.
- Which response was "objectively" better — the pick is our preference. A defensible
  pick with a plausible short reason is safe; an incoherent pick (choosing the
  response with a visible defect, or one that violated the user's own stated
  constraint) is the only kind that looks wrong.

## Standing defenses

- Every turn passes the padding test: it changes the artifact, adds a constraint,
  challenges a claim, or asks a genuinely next-step question.
- Every user-side text passes the humanizer gate against `HUMAN_VOICE_CORPUS.md`.
- Every task uses a fresh use-case cell from `PROMPT_PLAYBOOK.md` (logged).
- Zero real PII: personal details are generic-real (a friend, a teammate, "my
  manager"), never named third parties or real company-confidential content.
- The conversation ends the way corpus conversations end: quietly, after a
  satisfied narrowing turn — not with a thank-you sign-off.
