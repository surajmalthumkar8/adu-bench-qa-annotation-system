# TURN RULES — conversation flow, turn count, ending (binding)

## Counting (hard platform constraint)

- The initial prompt is **Turn 1**. Minimum **3** user turns, maximum **5**.
- After the first comparison, at least 2 more user messages are required.
- The state record (`../templates/STATE_TEMPLATE.md`) tracks the turn number; every
  deliverable states "this will be Turn N of 3–5".

## Every follow-up turn must earn its place (anti-padding)

A turn is valid only if it does at least one of:
- **Refines the artifact** — changes tone, length, adds a concrete detail, converts
  format (checklist), fixes what the model got wrong.
- **Adds or tightens a constraint** — "don't say gotta", "keep Sunday free",
  "under $50".
- **Challenges or probes the response** — "You specified 'globally', wasn't only one
  launch?", "but doesn't switching harm pattern recognition?".
- **Takes the genuine next step of the same goal** — "And how can I add it to a
  Token model", "Give me the service for create and deactivate tokens".

BANNED turns: "tell me more", "can you elaborate", "thanks, looks good", restating
the opening prompt, topic hops with no thread, any message written only to reach a
turn count. Research note: ~80% of real user follow-ups react to something specific
in the model's previous answer — ours must too, by quoting or pinpointing it.

## Reacting to the chosen response is mandatory

The turn-writer receives the chosen response and must anchor the follow-up to a
specific element of it (a word it used, an option it offered, a gap it left, a
question it asked back). A follow-up that could have been written without reading
the response is a defect.

## When the model's response has a flaw

Real users notice: a wrong fact, ignored constraint, or broken code in the CHOSEN
response is prime follow-up material ("you said X but...", "this errors on line...",
"I said no weekends"). Use it — error recovery is a strong authenticity signal.

## Ending (MODE END)

- End is allowed only at turn ≥3, and SHOULD happen as soon as the conversation
  feels complete — corpus norm is 3 turns; 5 only when genuinely needed.
- End the corpus way: the final turn is a small, satisfied, narrowing ask
  ("Perfect. One last thing...", "Just one short sentence I can add") — after its
  response, stop. **No thank-you sign-off, no goodbye turn** (zero exist in corpus;
  a goodbye message would waste a turn and read as padding).
- The END deliverable tells Suraj: make the final pick (if a pair is showing),
  send nothing further, submit.

## Multiple prompts per task

The platform allows trying a different prompt in the same task. Default: one
coherent conversation per task (all six references do this). Only start a second
thread if Suraj asks or the platform forces it; the same rules apply per thread.
