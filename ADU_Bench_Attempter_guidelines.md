
Annotation Hub

Home
Dashboard

Projects
ADU-Bench QA

Resources
Onboarding
Billing
Community Guidelines
Disputing a Review
Slack Guide
FAQ

Search...
⌘K
Need help?
Suraj Malthumkar

Sign out
ADU-Bench QA

Getting Started › Attempter Guidelines

1 / 3
Save & exit
Getting Started ·
Attempter Guidelines
Step-by-step instructions for verifying AI-generated answers against document evidence and submitting accurate QA verdicts.

01
Project Goal
What You Are Doing
Your task is to verify whether an AI-generated answer is correct based on the provided document evidence.
For each task you will see:

QUESTION
The question that was posed to the AI
AI-GENERATED ANSWER
The answer you need to verify
EVIDENCE PAGES
Pages from the source document in the left panel
PDF REFERENCE TAB
Original PDF images for tables, figures, and formulas
Your job is to decide whether the answer is supported by the evidence, then provide the exact evidence text that supports your judgment.

02
Task Workflow
Follow these steps for every task
1
Read the Question carefully.
2
Read the AI-generated Answer carefully.
3
Review all available Evidence Pages in the left panel.
4
Use the original PDF Reference tab when needed — especially for tables, figures, formulas, diagrams, or layout-sensitive text.
5
Decide whether the answer is Correct or Wrong.
6
Copy and paste the key evidence quote(s).
7
Enter the relevant evidence page number(s).
8
Add notes only if needed.
9
Submit the task.
03
QA Verdict: Correct vs Wrong
✅ CORRECT
Select Correct when the AI-generated answer is accurate and supported by the document evidence.
Use Correct when:
The answer directly matches the evidence.
The answer is a valid paraphrase of the evidence.
The answer gives the correct option for a multiple-choice question.
The answer is complete enough to satisfy the question.
The answer correctly identifies that the question is not answerable from the evidence.
❌ WRONG
Select Wrong when the AI-generated answer is incorrect, contradicted, incomplete, or unsupported by the evidence.
Use Wrong when:
The evidence says something different from the answer.
The answer includes information not found in the evidence.
The answer is only partially correct but misses required information.
The answer gives the wrong multiple-choice option.
The answer says not answerable, but the evidence does contain the answer.
The evidence is insufficient to confirm the answer.
Important: If you cannot verify the answer from the provided evidence, mark it Wrong. Do not rely on outside knowledge.
04
Evidence Quotes
The Evidence Quotes field is required. Copy and paste the exact text from the evidence that supports your verdict. Include enough context to make your decision clear.
FOR A CORRECT VERDICT
Paste the text that confirms the answer.
FOR A WRONG VERDICT
Paste the text that contradicts the answer, or the closest relevant evidence showing why it is unsupported.
Required Format
[DocX Page X] "exact evidence text"
Example:
[Doc1 Page 37] "Q.32 If the voltmeter in the given circuit reads 8 V, what is the resistance of the voltmeter?"
Do not write your explanation in the Evidence Quotes field. This field should contain quoted evidence from the document only.

Note on multiple documents: references must point to a document you find in the PDF Reference or in the titles inside the pages. Do not use the tab names.
05
Evidence Pages Used
List the page number or page numbers that contain the relevant evidence. Use only the pages you actually relied on for the verdict.
Format Examples
37
5, 6
12, 14, 15
Doc1: 5, 6 | Doc2: 3 (for cross-document tasks)
06
Notes Field
The Notes field is NOT optional. ALWAYS COMPLETE IT.
Add a note when:
The evidence is ambiguous.
The answer is partially correct but incomplete.
The PDF image and markdown text differ.
The relevant information appears in a table, figure, formula, or diagram.
Multiple pages were needed to verify the answer.
The answer format is close but not exact.
Example Note
"The answer captures the first part of Q.32, but the full referenced title includes the rest of the question, so I marked it Wrong."
07
Special Cases
MULTIPLE-CHOICE QUESTIONS
Check whether the selected option matches the evidence.
Select Correct only if the chosen option is supported.
Select Wrong if the selected option is not supported, even if the explanation contains some correct information.
"NOT ANSWERABLE" QUESTIONS
Some questions ask for information not in the evidence.
Select Correct only if the answer says not answerable AND you confirmed the evidence does not contain it.
Select Wrong if the evidence does contain the answer.
CROSS-DOCUMENT / MULTI-PAGE
Review all provided evidence tabs before deciding. Do not mark Wrong just because evidence is not on the first page. Check all available pages and the PDF reference.
TABLES, FIGURES, FORMULAS
Markdown evidence may not perfectly preserve visual structure. Use the PDF Reference tab to verify tables, figures, charts, diagrams, formulas, page layout, and captions. If the answer depends on visual layout, the PDF image is the final reference.
EXACT TITLE / REFERENCED QUESTION
When the question asks for the exact title, exact text, or referenced question, the full text must be present — not just part of it.

Example: The question asks for the exact title of Q.32. The evidence is "Q.32 If the voltmeter in the given circuit reads 8 V, what is the resistance of the voltmeter?" The AI answers only "If the voltmeter in the given circuit reads 8 V" — mark this Wrong because the full question text was omitted.
08
Common Mistakes to Avoid
Do not mark an answer Correct just because it sounds reasonable. Always verify against the evidence.
Do not use outside knowledge. Everything must be grounded in the provided evidence.
Do not rely only on the AI answer. Always check the evidence.
Do not ignore the PDF Reference when the answer depends on visual layout.
Do not provide page numbers without evidence quotes.
Do not paste huge blocks of text if only one sentence is needed.
Do not mark incomplete answers Correct when the question asks for exact text.
Do not assume an answer is wrong before checking all evidence pages.
Final Rule of Thumb
"Can I point to exact document evidence that proves this answer is correct?"
If yes, select Correct and paste the supporting quote.
If no, select Wrong.
Previous
Step 1 of 3

Next