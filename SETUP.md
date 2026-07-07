# SETUP — resume this system on another laptop (exact, self-validating)

This repo IS the system. Cloning it restores every agent, the humanizer skill, all
rules, workflows, knowledge, templates, the video pipeline, and the learning logs —
in the exact place Claude Code expects. Follow these steps; step 4 makes the machine
**prove** it arrived intact before you do any work.

## 0. Prerequisites (install once)
- **Git** and **Claude Code** (the CLI/IDE extension).
- **Python 3.12** (only needed to run the video-ingest pipeline + the verifier).
- Optional: **GitHub CLI** (`gh`) if you want to push changes back; **ffmpeg** on PATH
  for best video handling.

## 1. Clone the repo
```
git clone https://github.com/surajmalthumkar8/adu-bench-qa-annotation-system
cd adu-bench-qa-annotation-system
```
That single step restores everything Claude needs:
- `.claude/agents/` — all 8 subagents (6 DO_TASK-chain + 2 video), pinned `model: opus`.
- `.claude/skills/humanizer/` — the blader humanizer skill (v2.8.2).
- `system/` — rules, workflows, knowledge, templates, checklist, LESSONS.
- `video_pipeline/` — the ingest pipeline + its tools and LESSONS.
- `CLAUDE.md` — the project brain Claude Code reads on open.

Claude Code auto-discovers project agents (`.claude/agents/`) and project skills
(`.claude/skills/`) when you open this folder — nothing to register by hand.

## 2. Install the Python deps (only if you'll ingest recordings)
```
pip install -r video_pipeline/requirements.txt
```
Not needed just to DO tasks Suraj pastes into chat — only to run `ingest.py` on an mp4.

## 3. Restore the media from Google Drive (OPTIONAL)
The recordings and `ingest/` images were kept OUT of git (they're big; the verified
`reconstructed/*.md` evidence is already in the repo). You only need the media to
re-view old frames or re-ingest an old recording — **not** to continue working.
If you want them: from your Drive backup, copy each task's files back into the matching
folder, e.g. `Own_tasks/task6/Recording ....mp4` and (optionally) `Own_tasks/task6/ingest/`.
New tasks bring their own fresh recording, so you can skip this for day-to-day work.

## 4. Prove it arrived intact — the self-check
```
python verify_setup.py
```
Must end with **`RESULT: ALL REQUIRED CHECKS PASS`** (exit 0). It checks all 8 agents
(presence + `model: opus` + names), the humanizer skill (present, versioned, wired
mandatory), every rule/workflow/knowledge/template file, the 6-agent roster, and that
the python tools compile. Warnings about `cv2`/`numpy`/`rapidocr` are fine unless you're
ingesting video (then do step 2). Any `[FAIL]` line tells you exactly what's missing.

## 5. Open in Claude Code and paste the bootstrap prompt (below)
Claude then re-reads the system, runs the verifier itself, lists the agents + skill,
and runs a live smoke test of the humanizer agent+skill before you hand it a task.

---

## The bootstrap prompt (paste this into Claude Code on the new machine)

```
Bootstrap this project before we do any task. Do all of it, then report:

1. Read CLAUDE.md in full, plus the newest entries in system/learning/LESSONS.md and
   video_pipeline/learning/LESSONS.md, so you have the current state and rules.
2. Run `python verify_setup.py` and confirm it prints "ALL REQUIRED CHECKS PASS"
   (exit 0). If any FAIL, stop and tell me the exact line.
3. Confirm the subagents are registered by listing them: evidence-hunter,
   independent-solver, reviewer-simulator, humanizer, final-evaluator, lessons-scribe
   (+ doc-reconstructor, extraction-evaluator for video). Confirm the `humanizer`
   skill is available.
4. Smoke-test the humanizer agent+skill end-to-end: dispatch the humanizer agent on
   this deliberately AI-sounding note and confirm it (a) invokes the humanizer skill,
   (b) returns a concise, casual, corpus-voice note. Sample to humanize:
   "It is worth noting that the answer — namely option D — underscores the correct
   range, thereby illuminating the fact that it is fundamentally supported."
5. Confirm the full DO_TASK gate chain is ready (all 6 agents dispatch, gate order
   intact per WORKFLOW_RULES). Do NOT start a real task until steps 2 and 4 pass.

Report: verifier result, agent+skill list, the humanized sample output, and
"READY" or the exact blocker.
```

---

## Out-of-repo items (won't come with the clone — flagged so you're not surprised)
- `~/.claude/CLAUDE.md` — your **global** Research-Gateway rules (dispatch storm-researcher
  for external-knowledge tasks). Machine-global; copy it to the new machine's `~/.claude/`
  if you want that behavior. The project works without it.
- The live chat + auto-memory are local to the old laptop. The durable context lives in
  this repo: `CLAUDE.md` + both `LESSONS.md` files carry the state and every lesson.
- Your email + the client task content are public in this repo (as you chose). To scrub
  later: ask Claude to strip them and force-push.

## Troubleshooting
- `verify_setup.py` FAILs on an agent ⇒ the clone is incomplete; re-clone.
- Claude "doesn't see" an agent ⇒ make sure you opened the **repo root** (where `.claude/`
  lives) as the project folder, not a subfolder.
- `humanizer` skill not found by a subagent ⇒ the agent falls back to reading
  `.claude/skills/humanizer/SKILL.md` directly (built-in fallback); verify that file exists.
- Video ingest errors ⇒ run step 2 (`pip install -r video_pipeline/requirements.txt`).
