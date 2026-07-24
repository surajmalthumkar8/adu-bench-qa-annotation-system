# HUMAN VOICE CORPUS — real contributor user turns, verbatim

Every user-side message from the six signed-off reference transcripts
(`Interactive_contri_inst/reference_tasks/`). This corpus is the voice target for
every prompt and follow-up we write. The humanizer's test: would our turn blend in
here without standing out? New signed-off examples get appended verbatim.

## task-1 — writing help (cancel dinner message) — 5 user turns
1. "I need to cancel plans with a friend this Saturday because something came up at work. We were supposed to get dinner. Can you help me write a short message that sounds honest and apologetic, but not dramatic? I still want to reschedule soon."
2. "I like the short one better. Can you make it sound a little warmer? Also don't say "gotta" - that feels too casual for this friend."
3. "This is close. Can you suggest two nights next week in the message, like Tuesday or Thursday? I don't want to leave it totally open-ended."
4. "Perfect. One last thing, can you make a slightly shorter version I can send as a text? Same meaning, just fewer words."
5. "This works. Can you also give me one backup line in case they can't do Tuesday or Thursday? Just one short sentence I can add."

## task2 — coding interview prep advice — 3 user turns
1. "If i have a coding interview in 15 days and i am not that good at DSA but know the basics, what do you think is the best approach to get a good grasp on it?"
2. "Yes this is mostly for walmart but the thing is i always start at arrays but by the time i reach DP/Graphs i have lost interest and which is why i am very weak at them, so how to keep consistency?"
3. "but doesn't keeping on switching between topics harming the brain to learn/ recognize the pattern? as ultimately in interview recognizing the pattern is what is going to help?"

## task3 — factual lookup (Clash Royale) — 4 user turns
1. "When was the launche date for Clash Royale?"
2. "You specified "globally", wasn't only one launch? Or why this explanation?"
3. "Was this the first game of Supercell?"
4. "Which one of the Supercell games is the most popular?"

## task4 — weekly routine planning — 3 user turns
1. "I want to build a realistic weekly routine that balances work, exercise, errands, and downtime without feeling overly strict. Ask me a few questions about my current schedule, then create a flexible plan I can actually follow."
2. "I work 9 AM to 6 PM on weekdays. I want to exercise three evenings a week, do chores on weekends, and have one hour to relax each night. Please make me a simple weekly plan."
3. "This looks good, but I'd rather finish all chores on Saturday and keep Sunday mostly free. Can you revise the plan?"

## task5 — workday scheduling — 3 user turns
1. "I'm planning my workday tomorrow and have these priorities: reply to client emails, finish a project update, review a teammate's draft, and go to the gym after work. Can you help me organize this into a realistic schedule?"
2. "Can you make the schedule more flexible in case the project update takes longer than expected?"
3. "Can you turn it into a short checklist I can follow during the day?"

## task6 — Django error debugging — 3 user turns
1. (raw error paste, no prose at all)
   "auth.User.groups: (fields.E304) Reverse accessor 'Group.user_set' for 'auth.User.groups' clashes with reverse accessor for 'authentication.User.groups'.
           HINT: Add or change a related_name argument to the definition for 'auth.User.groups' or 'authentication.User.groups'."
2. "And how can I add it to a Token model fro tracking?"
3. "Give me the service for create and deactivate tokens by user"

## Voice fingerprint (distilled — the humanizer enforces this)

- **Length:** most turns are 8–45 words; a first prompt can run ~50. Nobody writes
  paragraphs. A developer may open by pasting a raw error with zero prose.
- **Openers acknowledge, never thank:** "I like the short one better." / "This is
  close." / "Perfect. One last thing," / "This works." / "This looks good, but" /
  "Yes this is mostly for walmart but". **Zero instances of "thanks", "thank you",
  greetings, or praise of the assistant** in the whole corpus.
- **Concrete, incremental asks:** one or two changes per turn ("make it warmer",
  "suggest Tuesday or Thursday", "fewer words", "turn it into a checklist").
- **They quote and push back on the response:** "don't say "gotta"" / "You
  specified "globally", wasn't only one launch?" / "but doesn't keeping on switching
  between topics harming the brain...?"
- **Imperfections are real and unforced:** lowercase "i", "walmart", "launche
  date", "fro tracking", a turn starting with "but", a hyphen used instead of a
  dash, comma splices, ESL-flavored phrasing ("Give me the service for create and
  deactivate tokens by user"). Never more than one or two per turn; never cartoonish.
- **No formatting ever:** no bullets, no numbered lists, no bold, no colons-then-list
  in user turns. Plain sentences only.
- **No em dashes, no semicolons, no "delve/moreover/furthermore"** — none appear in
  any real user turn.
- **Endings are quiet:** the conversation just stops after a satisfied turn; the
  last turn often narrows to one small final ask ("One last thing", "Just one short
  sentence I can add").
