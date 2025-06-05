import sys
import re
import fitz               # PyMuPDF

import spacy
nlp = spacy.load("en_core_web_sm")


# 1) Expanded list of clause headings (including synonyms/combined titles)
CLAUSE_TITLES = [
    "Termination",
    "Term and Termination",
    "Payment Terms",
    "Confidentiality",
    "Confidentiality Obligations",
    "Governing Law",
    "Dispute Resolution",
    "Governing Law and Dispute Resolution",
    "Force Majeure",
    "Liability",
    "Limitation of Liability",
    "Indemnification",
    "Definitions",
    "Term",
    "Intellectual Property",
    "Service Availability",
    "Monitoring and Reporting",
    "Support and Escalation Procedures"
]

# 2) Build regex patterns to match numbered or “Section X – …” prefixes
HEADING_PATTERNS = {}
for title in CLAUSE_TITLES:
    escaped = re.escape(title)
    pattern = re.compile(
        rf'^\s*(?:\d+[\.\)]\s*|Section\s+\d+\s*[\–\-\:]\s*)?{escaped}\b[:\-\s]?',
        flags=re.IGNORECASE
    )
    HEADING_PATTERNS[title] = pattern


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Opens a PDF via PyMuPDF (fitz) and concatenates all page text.
    Raises a clear error if fitz.open isn’t available.
    """
    if not hasattr(fitz, "open"):
        raise RuntimeError(
            "fitz.open is not available. "
            "Ensure you have installed PyMuPDF (pip install PyMuPDF) and "
            "that no other 'fitz' package is shadowing it."
        )

    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text() + "\n"
    return text


def extract_text_from_txt(txt_path: str) -> str:
    """
    Reads a .txt file and returns its entire contents as a single string.
    """
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_clauses(raw_text: str) -> dict:
    """
    Given the full document text (from PDF or TXT), split into lines and:
    1) Scan each line for a heading match (using HEADING_PATTERNS).
    2) Record (line_index, heading_title) for each match.
    3) For each match, collect all lines from that line up to the next heading line.
    4) Return a dict: { "Termination": "…full clause text…", … }.
    """
    lines = raw_text.splitlines()
    occurrences = []

    # 1) Find every line that matches any heading pattern
    for i, line in enumerate(lines):
        for title, pattern in HEADING_PATTERNS.items():
            if pattern.match(line):
                occurrences.append((i, title))
                break

    # 2) If no headings found, return empty dict
    if not occurrences:
        return {}

    # 3) Sort by line index
    occurrences.sort(key=lambda x: x[0])

    clauses = {}
    total_lines = len(lines)

    # 4) Slice out each clause block
    for idx, (start_idx, title) in enumerate(occurrences):
        # Determine end index
        if idx + 1 < len(occurrences):
            end_idx = occurrences[idx + 1][0]
        else:
            end_idx = total_lines

        clause_lines = lines[start_idx:end_idx]
        clause_text = "\n".join(clause_lines).strip()

        # Append if same heading appears multiple times
        if title in clauses:
            clauses[title] += "\n\n" + clause_text
        else:
            clauses[title] = clause_text

    return clauses
