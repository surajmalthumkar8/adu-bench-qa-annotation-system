# PROJECT MODEL — ADU-Bench QA Verification

> The single mental model of how this project works. If a future doc contradicts this,
> update this file and log the change in `system/learning/LESSONS.md`.

## 1. What the project is

**ADU-Bench QA Verification** (v3 at time of onboarding): for each task, an AI model was
asked a question about one or more source documents (scientific/technical books, mostly
World Scientific publications). Our job is to **verify whether the AI-generated answer is
correct using ONLY the document evidence provided in the task** — never outside knowledge.

The output of every task is four fields:

| Field | Content |
|---|---|
| **QA Verdict** | `Correct` or `Wrong` — binary, no middle ground |
| **Evidence Quotes** | Verbatim quotes from the evidence, cited `[DocX Page Y] "..."` |
| **Evidence Pages Used** | Minimal list of pages actually relied on (`Doc1: 4 | Doc2: 4`) |
| **Notes** | Short prose explanation of the reasoning (labeled optional — **always required**) |

## 2. Why quality is existential

- Every submission becomes benchmark data. A wrong verdict poisons the dataset.
- Quality record is cumulative and directly controls workload:
  - **Task Wall**: first 3–5 tasks on a new project need an average score **> 4/5** to continue (one retry allowed).
  - **Minimum overall score: 3.5** to stay on a project.
  - Repeated SBQs (send-backs) trigger standing review; there is no reset.
- Reviewers work from the same instructions we do. There is no hidden standard —
  the guidelines ARE the rubric.

## 3. The two platforms (operational reality)

Work happens on **two systems simultaneously, which must stay in sync**:

1. **Annotation Platform (Henna)** — task claiming, Attempt URL, scores, feedback, daily limits.
   `https://annotation-platform-henna.vercel.app/dashboard`
2. **Feather** — where the actual annotation form is filled and submitted.
   Hierarchy: Campaign → Task Batch → Task. Statuses: Unclaimed → In progress →
   Completed → In review → (Needs work → Fixing done →) Signed off.

Hard operational rules (violations lose work/pay):
- Claim on Henna → open Task Variables link → **claim in Feather** → copy the *post-claim*
  Feather URL into Henna's **Attempt URL** field (the task ID in the URL changes after claiming).
- Actions must mirror: Submit in Feather ⇔ Submit on Henna; Release ⇔ Release. Never cross them.
- **NEVER** use `Cancel task` or `Escalate issue` in Feather. Problems → Release + post in #general.
- Claim time limit: **4× AHT**. Overrun ⇒ unassigned, work lost, unpaid.
- Timeouts and admin releases count against the daily limit; voluntary releases don't.
- If a task is not "Unclaimed" in Feather when you open it: do nothing in Feather, answer
  **No** to "Could you submit this task in Feather?" on Henna, Release, report in #general.

## 4. Roles and lifecycle

- **Attempter** produces the first version. The reviewer can improve a good foundation but
  cannot rescue a lazy one.
- **Reviewer** re-verifies within a ~5-minute budget: verdict logic, quote verbatim-ness,
  page accuracy, note presence. Approve / Improve-and-approve / Reject with actionable feedback.
  Approving bad work is itself a quality failure.
- **SBQ / Needs work**: read ALL feedback, re-read instructions, fix EVERY issue, use
  **Make edits → Mark as fixed** in Feather. Open the task via the **Attempt URL** from Task
  History, NOT the original Task Variables link.

## 5. Evidence environment

- Left panel: evidence tabs with markdown extractions of document pages
  (tab labels like `Doc1 P5-6 / Doc2 P1` can span documents — cite per-document pages, not tab names).
- Last tab: **PDF Reference** — original page images. This is the **final source of truth**
  for tables, figures, formulas, layout, and whenever markdown is broken.
- Tasks are frequently **cross-document** (2–5 docs). Page numbers restart per document.
- When the markdown is unreadable and you must quote from the PDF image, prefix the
  resource name inside the bracket: `[<pdf name> Page X] "..."`.

## 6. Operating mode (how this system is actually used)

Suraj claims tasks on the platforms and **pastes the task content + screenshots into
chat; Claude does the task** and returns a paste-ready submission
(`workflows/DO_TASK.md` → `templates/DELIVERABLE_TEMPLATE.md`). Claude never touches
Henna/Feather directly; the platform rules in §3 are context Suraj executes by hand.
Implication: input completeness cannot be assumed — DO_TASK step 1 gates on it, and
decisive values in screenshots are transcribed character-by-character.

## 7. Support structure

Order of escalation: re-read instructions → search Slack history/pins → ask in
`#[project]-general` (with task number + expected vs actual + screenshot) → project lead →
war room when active. Announcement channels are staff-only. QMs group handles
login/password/access issues (Annotation Hub first-time password: `123456`, change it).
