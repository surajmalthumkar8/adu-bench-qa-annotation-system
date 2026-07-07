#!/usr/bin/env python3
"""Deterministic pre-submission validator for ADU-Bench QA submissions.

Usage:
    python tools/validate_submission.py <submission.md>
    python tools/validate_submission.py --verdict Correct --quotes-file q.txt \
        --pages "Doc1: 4 | Doc2: 4" --notes-file n.txt

Submission .md format (same as templates/SUBMISSION_TEMPLATE.md):
    ## Verdict / ## QA Verdict        -> Correct | Wrong
    ## Evidence Quotes                -> [DocX Page Y] "..." blocks
    ## Evidence Pages Used            -> Doc1: 5, 6 | Doc2: 3   (or bare numbers)
    ## Notes                          -> prose

Exit code 0 = clean, 1 = findings (printed one per line, reviewer style).
These checks mirror the reviewer's minute-5 format pass plus internal consistency
invariants from system/rules/EVIDENCE_RULES.md.
"""
import argparse
import re
import sys

CITE_RE = re.compile(
    r"\[(?:(?P<doc>Doc\s?\d+|[\w.\- ]+?\.pdf)[,\s]+)?Page\s+(?P<page>\d+)\]\s*:?\s*"
    r"[\"“‘']", re.IGNORECASE)
EXPLANATION_STARTS = (
    "the answer", "this shows", "this is", "therefore", "so ", "because",
    "it means", "which means", "this confirms", "the response",
)


def parse_sections(text):
    sections = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s*(?:[^\w\s]*\s*)?(.+?)\s*$", line)
        if m and re.search(r"verdict|evidence quotes|pages used|notes", m.group(1), re.I):
            key = m.group(1).lower()
            if "verdict" in key:
                current = "verdict"
            elif "quotes" in key:
                current = "quotes"
            elif "pages" in key:
                current = "pages"
            elif "notes" in key:
                current = "notes"
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
    return {k: "\n".join(v).strip().strip("`").strip() for k, v in sections.items()}


def extract_cited_pages(quotes):
    """Return set of (doc_label_or_None, page) from citation brackets."""
    cited = set()
    for m in re.finditer(r"\[([^\]]+)\]", quotes):
        inner = m.group(1)
        pm = re.search(r"Page\s+(\d+)", inner, re.I)
        if not pm:
            continue
        dm = re.search(r"(Doc\s?\d+)", inner, re.I)
        doc = dm.group(1).replace(" ", "").capitalize() if dm else None
        if not dm:
            # pdf-name citation (broken-markdown case) — treat name as doc label
            nm = re.match(r"\s*([\w.\- ]+?\.pdf)", inner, re.I)
            doc = nm.group(1).strip() if nm else None
        cited.add((doc, int(pm.group(1))))
    return cited


def extract_pages_field(pages):
    """Return set of (doc_label_or_None, page) from the pages-used field."""
    out = set()
    pages = pages.strip()
    if not pages:
        return out
    if re.search(r"Doc\s?\d+\s*:", pages, re.I):
        for part in pages.split("|"):
            dm = re.match(r"\s*(Doc\s?\d+)\s*:\s*(.+)", part.strip(), re.I)
            if not dm:
                continue
            doc = dm.group(1).replace(" ", "").capitalize()
            for n in re.findall(r"\d+", dm.group(2)):
                out.add((doc, int(n)))
    else:
        for n in re.findall(r"\d+", pages):
            out.add((None, int(n)))
    return out


def validate(verdict, quotes, pages, notes):
    findings = []

    # Verdict
    if verdict.strip().lower() not in ("correct", "wrong"):
        findings.append(f"Verdict must be exactly 'Correct' or 'Wrong' (got: '{verdict.strip() or 'EMPTY'}').")

    # Quotes present + format
    if not quotes.strip():
        findings.append("Evidence Quotes field is empty. Paste the verbatim quote(s).")
    else:
        if not CITE_RE.search(quotes):
            findings.append('No citation matching [DocX Page Y] "..." found in Evidence Quotes.')
        if re.search(r'\.\.\."?\s*$', quotes.strip()) or re.search(r'"\s*\.\.\.', quotes):
            findings.append("Possible truncated quote ('...'). Quotes must be complete sentences.")
        first_line = quotes.strip().splitlines()[0].strip().lower()
        if not first_line.startswith("[") and first_line.startswith(EXPLANATION_STARTS):
            findings.append("Evidence Quotes appears to start with explanation text. Quotes only — move reasoning to Notes.")

    # Pages field present + consistency with citations
    cited = extract_cited_pages(quotes)
    listed = extract_pages_field(pages)
    if not listed:
        findings.append("Evidence Pages Used field is empty or unparseable.")
    elif cited:
        # normalize: if either side lacks doc labels, compare page numbers only
        if any(d is None for d, _ in cited) or any(d is None for d, _ in listed):
            cited_n = {p for _, p in cited}
            listed_n = {p for _, p in listed}
        else:
            cited_n, listed_n = cited, listed
        missing = cited_n - listed_n
        padded = listed_n - cited_n
        if missing:
            findings.append(f"Pages cited in quotes but missing from Pages Used: {sorted(missing, key=str)}.")
        if padded:
            findings.append(f"Pages listed in Pages Used but never quoted (padding): {sorted(padded, key=str)}.")

    # Notes
    if not notes.strip():
        findings.append("Notes field is empty. Notes are ALWAYS required on this project.")
    else:
        n_sentences = len(re.findall(r"[.!?](\s|$)", notes))
        if len(notes.split()) > 130:
            findings.append(f"Note is long ({len(notes.split())} words). Target 1-4 tight sentences.")
        if n_sentences == 0:
            findings.append("Note has no complete sentence.")
        for tell in ("furthermore", "moreover", "it is worth noting", "delve", "as an ai"):
            if tell in notes.lower():
                findings.append(f"AI-tell phrase in note: '{tell}'. Humanize it.")
        if verdict.strip().lower() == "wrong" and not re.search(
                r"incomplete|contradict|does not|missing|only|absent|no evidence|cannot|not (?:found|present|mention)", notes, re.I):
            findings.append("Wrong verdict but the note doesn't name the defect (contradiction/incompleteness/unsupported).")

    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="submission markdown file")
    ap.add_argument("--verdict")
    ap.add_argument("--quotes-file")
    ap.add_argument("--pages")
    ap.add_argument("--notes-file")
    args = ap.parse_args()

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            s = parse_sections(f.read())
        verdict = s.get("verdict", "")
        quotes = s.get("quotes", "")
        pages = s.get("pages", "")
        notes = s.get("notes", "")
    else:
        verdict = args.verdict or ""
        quotes = open(args.quotes_file, encoding="utf-8").read() if args.quotes_file else ""
        pages = args.pages or ""
        notes = open(args.notes_file, encoding="utf-8").read() if args.notes_file else ""

    findings = validate(verdict, quotes, pages, notes)
    if findings:
        print(f"REJECT — {len(findings)} finding(s):")
        for f_ in findings:
            print(f"  - {f_}")
        sys.exit(1)
    print("CLEAN — all deterministic checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
