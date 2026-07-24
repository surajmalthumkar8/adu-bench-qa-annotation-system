# PROMPT PLAYBOOK — authentic prompt seeds + rotation discipline

Used in DO_TASK MODE START when Claude must supply the opening prompt. Goal: every
task opens with a fresh, genuinely everyday prompt that supports 3–5 natural turns,
and no two tasks ever look alike. Log every used prompt in
`../learning/PROMPT_LOG.md` (date, task id, category, opening line) BEFORE delivering.

## Rotation rule (binding)

Pick the category least-recently used in PROMPT_LOG. Within a category, never reuse
a scenario, artifact type, or named detail that appears in the log. The instructions
flag "repetitive tasks" — rotation is our defense.

## Categories and seed shapes (instructions §3 + corpus)

Each seed is a SHAPE, not a script — the turn-writer instantiates it with fresh,
concrete, scrubbed-real details and the humanizer gives it the corpus voice.

### 1. Writing help (corpus: task-1)
- Rework a real message: cancel/reschedule with a friend, decline an invite, follow
  up on a landlord/neighbor issue, ask a professor/manager for something — with tone
  constraints ("honest but not dramatic").
- Improve an email/cover letter/LinkedIn blurb; "make it sound like me, less stiff".
- Multi-turn arc: draft → tone tweak → concrete detail added → shorter version.

### 2. Coding questions (corpus: task2, task6)
- Paste a raw error/traceback with no prose (strong signal) — Python/Django/JS/SQL.
- "Why is my function returning None?" style bug asks with a small snippet.
- Practical dev decisions: "how do I make this query faster", token/auth patterns,
  "is it bad practice to X".
- Multi-turn arc: fix → extend ("And how can I add it to..."), → "Give me the
  service/util for X" → edge case question.

### 3. Summarizing / explaining (instructions table; corpus: task3 adjacent)
- "Explain compound interest simply", "What is a neural network?", explain a term
  the user "keeps seeing" — then challenge or narrow ("wasn't only one launch?",
  "explain like I'm emailing this to my team").
- Factual lookups about a product/game/show the persona actually uses, with
  follow-up curiosity chain.

### 4. Brainstorming (instructions table)
- Team offsite ideas, saving money on groceries, birthday gift under a budget,
  weekend trip options nearby, what to cook with what's in the fridge.
- Multi-turn arc: options → constrain ("under $50", "no outdoor stuff") → pick one
  and go deeper → final concrete artifact (list, plan, message).

### 5. Planning / productivity (corpus: task4, task5)
- Weekly routine balancing work/gym/errands/downtime; tomorrow's workday around
  4 real priorities; study plan around a deadline.
- The "ask me a few questions first" opener is gold — it guarantees a real exchange.
- Multi-turn arc: plan → revise one preference → convert format (checklist).

## Persona discipline

Stay ONE plausible person per task (a working professional who codes a bit, plans
their week, texts friends, plays mobile games). Details are generic-real: "a friend",
"my teammate", "Saturday", "9 to 6". Never real names, employers, addresses, or
anything from Suraj's actual life/PII. Company names only as public consumer facts
(interviewing at Walmart-scale retailer, playing Clash Royale) — fine per corpus.

## Prompt quality bar (all must hold)

- Would a person actually type this into ChatGPT on a Tuesday? (No trick questions,
  no benchmark-style puzzles, no artificial difficulty.)
- Does it carry at least one concrete personal detail that makes it real?
- Can it sustain 3–5 turns of genuine refinement/curiosity without padding?
- Is it under ~60 words, unformatted, in the corpus voice (imperfections allowed)?
