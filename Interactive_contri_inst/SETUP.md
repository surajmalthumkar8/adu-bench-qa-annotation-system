# SETUP — SxS Interactive system on a new laptop

Everything the system needs travels inside this repo: the engineered system
(`system/`), the seven `sxs-*` agents (`.claude/agents/`), the validators
(`tools/`), the source-of-truth instructions + 6 reference transcripts, and the
repo `CLAUDE.md` routing. Cloning the repo IS the setup; the steps below just
verify it and wire up Claude Code.

## Prerequisites on the new laptop

1. **Git** + access to `github.com/surajmalthumkar8/adu-bench-qa-annotation-system`
2. **Python 3.8+** on PATH (`python --version`)
3. **Claude Code** installed and logged in
4. Recommended: the blader **humanizer skill** at `.claude/skills/humanizer/`
   (repo-local). If it travels with the repo you're done; if not, reinstall it —
   the sxs-humanizer agent has a documented fallback but the skill is preferred.

## Steps

```bash
git clone https://github.com/surajmalthumkar8/adu-bench-qa-annotation-system.git annotation_LinkedIn
cd annotation_LinkedIn
python Interactive_contri_inst/tools/verify_sxs_setup.py   # must print SETUP OK
claude   # start Claude Code IN THIS FOLDER (repo root), so CLAUDE.md + agents load
```

Then paste the **first-run prompt** below into Claude Code once. After that,
day-to-day usage is just pasting task content — the routing in `CLAUDE.md` does
the rest.

## First-run prompt (paste into Claude Code on the new laptop)

```
This repo contains three annotation projects; I work the SxS Interactive
Preference Collection project (Interactive_contri_inst/). Set yourself up:

1. Read CLAUDE.md (project routing) and Interactive_contri_inst/system/ in this
   order: knowledge/PROJECT_MODEL.md, rules/WORKFLOW_RULES.md (note FAST MODE is
   the default), rules/PREFERENCE_RULES.md, rules/TURN_RULES.md,
   rules/AUTHENTICITY_RULES.md (note my standing instruction at the top),
   workflows/DO_TASK.md, knowledge/HUMAN_VOICE_CORPUS.md,
   knowledge/GOLD_PATTERNS.md, learning/LESSONS.md, learning/PROMPT_LOG.md.
2. Run: python Interactive_contri_inst/tools/verify_sxs_setup.py - it must print
   SETUP OK. Fix anything it flags before continuing.
3. Confirm the seven sxs-* agents in .claude/agents/ are available and pinned
   model: opus. Confirm the humanizer skill resolves via the Skill tool.
4. Check Interactive_contri_inst/sessions/ for any OPEN task state from my other
   laptop and tell me if one exists (I may be resuming it).
5. Reply with: SETUP OK/ISSUES, the current PROMPT_LOG categories used so far,
   any open session, and one line confirming you will (a) run DO_TASK on every
   paste in FAST MODE, (b) always humanize every user-side word against the
   corpus, (c) always anchor turns to the previous answer, (d) deliver picks fast.

Then wait. From my next message on, I paste task content and you run
Interactive_contri_inst/system/workflows/DO_TASK.md on it - no preamble.
```

## Daily flow reminder (both laptops)

- Paste task intro → get the opening prompt. Paste A/B pairs → get PICK + reason +
  next turn. 3-5 user turns, end naturally, submit.
- **Type** deliverables into the platform, don't paste big blocks (telemetry).
- Commit + push `Interactive_contri_inst/sessions/` and `system/learning/` after
  working sessions so state and lessons stay synced between laptops:
  `git add Interactive_contri_inst && git commit -m "sxs: session sync" && git push`
  and `git pull` before starting on the other machine.

## Post-check (any time)

`python Interactive_contri_inst/tools/verify_sxs_setup.py` — verifies all 18
system files, both validators, the 7 Opus-pinned agents, the 6 reference
transcripts, and runs the turn validator on a sanity sample. SETUP OK = ready.
