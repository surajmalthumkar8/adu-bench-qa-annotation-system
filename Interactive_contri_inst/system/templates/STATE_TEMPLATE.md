# STATE TEMPLATE — per-task conversation state

One file per task at `Interactive_contri_inst/sessions/<task-id>_state.md`,
updated at every paste BEFORE the deliverable goes out. Archived (kept, marked
CLOSED) at MODE END.

```markdown
# Task state: <task-id or short label>   [OPEN|CLOSED]

- Started: <date>
- Category: <playbook category> · Persona: <one line>
- Planned arc: <one line, updated as it evolves>

## Turn ledger
| Turn | User message (verbatim) | Pick | Decisive differential |
|---|---|---|---|
| 1 | ... | A | ... |

## Constraint ledger (accumulates; every future response is checked against ALL)
- T1: <constraint>
- T2: ...

## Chosen-response memory (what the model has already said/committed to)
- T1: <key facts, artifacts, offers made>

## Notes
- <anything unusual: resamples, near-ties, reviewer risks>
```
