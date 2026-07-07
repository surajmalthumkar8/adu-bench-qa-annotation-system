# NOTE STYLE CORPUS — how teammates actually write (verbatim, from signed-off tasks)

The humanizer and final-evaluator agents ground every note in THIS corpus. A note that
wouldn't blend into this list is not done. When new signed-off tasks land in
`Others_tasks/`, append their notes here verbatim and refresh the fingerprint.

## The 16 signed-off notes, verbatim

1. "This is Correct. In Computer-Aided Design of Communication Networks the author is listed as Wai-Kai Chen with the affiliation University of Illinois at Chicago, using the preposition at. In Feedback Networks the same author appears as W K Chen with the affiliation University of Illinois, Chicago, where the preposition has become a comma, so the aligning entry is W K Chen at University of Illinois, Chicago exactly as the answer states."
2. "Manufacturing appears as the completion of the chapter title on Doc2 page 9 and is absent from the Mobile Robot Path Planning chapter title on Doc3 page 12."
3. "The actual duration adds up to 57 days, since ICTP Trieste ran for 20 days and University of Sydney ran for 4 days while CIRM Marseille ran for 33 days. If Trieste and Sydney each lasted 33 days like Marseille, the total would reach 99 days, so the counterfactual total is 42 days higher than the actual total."
4. "Option D matches the evidence because Doc1, written by Jean-Paul Brasselet, states on page 91 that Theorem 5.2 gives χ(X) = ΣI(v,a_i), the vector field index term used throughout that paper, while Doc2 page 38 gives Lemma 6.1 in the MacPherson classes section as Σn_αEu_x(V̄α) = 1, with Eu denoting the local Euler obstruction tied to MacPherson's construction. The same Doc2 page defines the Mather class using c^*(Θ̃) as the usual total Chern class of the bundle, making Chern class the shared term option D names."
5. "The PDG[22] tritium beta-decay electron-antineutrino limit is 15 eV (Doc1) and KATRIN's 90% CL projected sensitivity is 0.2 eV (Doc2). Dividing gives 15 / 0.2 = 75."
6. "The narrative dates Maxwell's equations to 1873 and the Earnshaw ether quotation to 1842, both in the 19th century, so the same-century pairing in C is supported, so I marked it Correct."
7. "Fixed-Film delay = 325 - 1 = 324, Activated Sludge delay = 465 - 1 = 464. The difference is 464 - 324 = 140."
8. "The response correctly identifies the versions of the 2 volumes (12 and 29) and subtracts them to find the volume gap of 17, this was the users request. Answer matches document evidence."
9. "The book's contents list the melting transition, the solid line first order transition from the Doc1 phase diagram, as section 6.1.8 on page 189, which matches the answer."
10. "Answer is incomplete, it just says "u; v; w" but it does not mention which columns & rows are involved in the operation"
11. "The 10 ZMP training systems on page 11 of Doc2 plus the 9 small molecules of the cc-pVTZ VIP test on page 90 of Doc3 give a subtotal of 19, which matches the AI answer; the Doc1 QCISD study has no stated count and is excluded as the question requires."
12. "The answer is supported because Doc1 page 5 identifies Theory of Formal Languages with Applications and gives Copyright © 1999 by World Scientific Publishing Co. Pte. Ltd. Doc2 page 5 identifies Algebraic Theory of Automata and Language and gives Copyright © 2004 by World Scientific Publishing Co. Pte. Ltd. Since 2004 is 5 years later than 1999, option C is correct."
13. "The answer is supported because Doc1 page 5 shows Focus on Multidimensional Microscopy with Copyright © 1999 by World Scientific Publishing Co. Pte. Ltd. and identifies Vol. 1 by ISBN. Doc2 page 5 shows the same title with Copyright © 1999 by World Scientific Publishing Co. Pte. Ltd. and identifies Vol. 2 by ISBN. Therefore, both volumes have the same copyright year, 1999, matching option C."
14. "The Published list on Doc5 page 3 runs from Volume 12 down to Volume 5, so of the sampled titles Volumes 7, 9 and 12 appear but Volumes 1 and 2 do not. The Answer names those two missing titles, so it is correct."
15. "The relevant volume labels are 4, 7, and 12. The mean of 4 and 7 is 5.5, and 12 - 5.5 = 6.5, matching the expected answer."
16. "The answer is correct. Using only the print ISBN-13 values gives a range of 6888, with Selected Topics as the maximum and Basic Views as the minimum.
    Using only the print/hardcover ISBN-13 values (excluding the set ID and all e-books):
    Selected Topics suffix = 9558
    Quantized Structures suffix = 2694
    Basic Views suffix = 2670
    Range = 9558 − 2670 = 6888, so the maximum is Selected Topics and the minimum is Basic Views."

## Style fingerprint (what makes these read human)

**Structure**
- 1–4 sentences of continuous prose; ONE note (16) uses short labeled calc lines — only
  acceptable when arithmetic has 3+ operands.
- No headers, no bullets, no bold, no intro/outro. The note starts mid-argument.
- Openers used: "This is Correct." / "The answer is supported because..." /
  "The answer is correct." / "Answer is incomplete, ..." / or straight into the fact
  ("Manufacturing appears as...", "Fixed-Film delay = 325 - 1 = 324").

**Voice**
- Declarative and confident; zero hedging (no "seems", "likely", "appears to suggest").
- Occasional first person past tense: "so I marked it Correct." Natural, sparing.
- Long connected sentences glued with "so", "since", "while", "which matches" — NOT
  "furthermore/moreover/additionally".
- **Human imperfections occur and are fine**: comma splices ("...gap of 17, this was
  the users request"), missing apostrophes, "&", "2 volumes" (digit not word), a Wrong
  note with no closing period (10). Do not polish these into corporate English; do not
  fake typos either — just don't over-correct natural roughness.

**Content habits**
- Evidence anchored inline as "Doc2 page 9" / "page 5" / "on page 91" — lowercase page,
  no brackets in the note.
- Every number in the verdict chain shown with its arithmetic: "15 / 0.2 = 75",
  "12 - 5.5 = 6.5", "465 - 1 = 464".
- Wrong verdicts name the defect bluntly and quote the offending fragment:
  'it just says "u; v; w"'.
- Exclusion clauses from the question get echoed ("excluded as the question requires",
  "Using only the print ISBN-13 values").
- References to the answer as "the answer", "the Answer", "the AI answer", or
  "the response" — varies, all fine.

**Never present in the corpus** (instant AI-tells to strip)
- "It is worth noting", "Furthermore", "Moreover", "Overall", "In conclusion",
  "aligns with", "delve", "comprehensive", "crucial".
- Rule-of-three constructions, em-dash asides, semicolon chains (one exception: note 11
  uses a single semicolon — one is fine, a pattern is not).
- Meta-language about process ("After reviewing the evidence...", "Upon verification...").
- Restating the question before answering it.
