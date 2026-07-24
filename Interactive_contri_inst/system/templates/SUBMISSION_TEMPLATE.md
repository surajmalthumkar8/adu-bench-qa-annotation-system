# SUBMISSION TEMPLATE — internal per-paste record (validated file)

The validator (`tools/validate_sxs_turn.py`) runs on a file in exactly this shape.
Sections in this order. PICK/REASON/NEXT MESSAGE hold ONLY paste-ready text — no
commentary inside them.

```markdown
## MODE
START | COMPARE | SINGLE | END

## TURN
N of 3-5            <!-- the turn number the NEXT MESSAGE will be; for END: "END at N" -->

## PICK
A | B | N/A         <!-- N/A only for START and SINGLE -->

## REASON
<optional platform note, 1-2 casual sentences, or "N/A">

## NEXT MESSAGE
<the exact user message Suraj will type — or "END - send nothing further, submit">

## INTERNAL (not pasted — verification record)
- Decisive differentials: <quoted facts that decided the pick; or N/A>
- Near-tie: yes/no
- Bias check: length-neutralized / format-neutralized / position-neutralized /
  sycophancy-checked
- Constraint ledger: <every constraint set so far and whether the chosen response
  honored each>
- Turn anchor: <the specific element of the chosen response this turn reacts to>
- Arc position: <where we are in the planned arc; end plan>
- Persona/PII scan: clean
- Gates: validator=<CLEAN> reviewer-simulator=<APPROVE> humanizer=<applied+skill;
  tells removed: <what the humanizer stripped, e.g. tidy parallel clause / formal
  closer; or "none"> > final-evaluator=<SHIP>
```
