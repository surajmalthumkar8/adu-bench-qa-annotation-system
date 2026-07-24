# AUTHENTICITY RULES — every user-side word must read human-typed (binding)

Applies to: opening prompts, every follow-up turn, and the optional preference
reason. Enforced by sxs-humanizer (always runs the blader `humanizer` skill),
mechanically checked by `tools/validate_sxs_turn.py`, and validated by
sxs-reviewer-simulator + sxs-final-evaluator against
`../knowledge/HUMAN_VOICE_CORPUS.md`.

## Standing instruction (Suraj, 2026-07-24 — binding on every user-side text)

Every prompt and follow-up MUST be: (1) humanized — run through the humanizer, never
AI-sounding; (2) casual — like a person typing, not composing; (3) anchored to the
previous answer — quote or react to something specific the model just said (the way
task-1 says "don't say gotta" and task3 says "You specified globally"); and
(4) styled on the reference-task user turns in HUMAN_VOICE_CORPUS.md. No exceptions,
fast mode included — the humanizer dispatch is never the step that gets cut.

## The one test

Would this message blend into HUMAN_VOICE_CORPUS.md without standing out — in
length, register, punctuation, and imperfection level? If it sounds composed,
polished, or "smart", it fails. Plainer beats cleverer, always.

## Hard bans in user-side text (validator FAILs)

- Em dashes (—) and en dashes (–); curly quotes; ellipsis character (…).
- Any formatting: bullets, numbered lists, bold, headings, markdown of any kind.
  (Exception: a pasted code snippet/error as the prompt itself, task6-style.)
- AI-tell vocabulary: delve, crucial, pivotal, moreover, furthermore, additionally,
  comprehensive, leverage, utilize, robust, nuanced, underscore, testament,
  intricate, tapestry, vibrant, enhance, streamline, foster, "I appreciate",
  "certainly", "kindly".
- Rule-of-three constructions and negative parallelism ("not just X, but Y").
- Thanking, greeting, or praising the assistant ("thanks!", "great answer") — zero
  instances exist in the corpus.
- Over 80 words (corpus max ≈ 55; opening prompts ≤ ~60, follow-ups usually ≤ 45).

## Soft rules (validator WARNs; humanizer judgment)

- Semicolons and colons: real users almost never use them — avoid.
- Perfect balanced punctuation across a long turn reads composed — vary it.
- Contractions on ("I'd", "don't"); fragments allowed ("Same meaning, just fewer
  words."); starting with "but"/"And" allowed and corpus-attested.
- Word repetition is human — do not synonym-cycle.

## Imperfections — allowed, never forced

Corpus-real: lowercase "i", lowercase brand names ("walmart"), a small typo
("launche", "fro tracking"), a comma splice, slightly bent grammar ("Give me the
service for create and deactivate tokens"). Budget: **at most 1–2 light
imperfections per turn, and many turns with none.** Never misspell in a way that
changes meaning; never fake incompetence; never repeat the same typo pattern across
turns (that reads scripted). The humanizer decides where, if anywhere, one lands.

## Persona & PII

- One consistent plausible persona per task (see PROMPT_PLAYBOOK). Details are
  generic-real: "a friend", "my teammate", "Saturday", "9 to 6".
- ZERO real PII: no real names of private people, employers, addresses, emails,
  phone numbers, confidential material. Public consumer facts (Walmart, Clash
  Royale) are fine — the corpus uses them.
- Never anything traceable to Suraj's real life or clients.

## Reason field register

First person fine, casual, 1–2 sentences, specific ("A kept the message shorter
like I wanted"). Same bans as above. Must not read like a rubric or repeat wording
used in previous tasks.

## Cross-task variety (anti-fingerprint)

Vary across tasks: turn lengths, opener styles (not every task starts "Can you"),
imperfection placement, reason phrasing. Any pattern repeated 3 tasks running is a
LESSONS-level defect — scripts get flagged; humans vary.
