"""
Extract contact info, skills, and general text from resumes
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional

# ---------------- Exceptions ----------------
class ParseError(Exception): ...
class EmptyTextError(ParseError): ...
class EncryptedOrCorruptPDF(ParseError): ...

# ---------------- Regexes (simple + robust) ----------------
CTRL_RE = re.compile(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]")
WS_RE   = re.compile(r"[ \t\f\v]+")
LIGS    = {"ﬁ":"fi","ﬂ":"fl"}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s\-\.]?)?(?:\(?\d{3}\)?[\s\-\.]?)\d{3}[\s\-\.]?\d{4}")
# We only store links if the line contains these domains (per your rule)
LINKEDIN_LINE_RE = re.compile(r"linkedin\.com/[^\s|,;]+", re.IGNORECASE)
GITHUB_LINE_RE   = re.compile(r"github\.com/[^\s|,;]+",   re.IGNORECASE)
BULLET_MARKERS = ("•", "-", "–", "—", "*", "∙", "·")

_WORD = re.compile(r"\w+")
_SKILLS_WORD = re.compile(r"\bskills?\b", re.IGNORECASE)
_CATEGORY_LINE = re.compile(r"^\s*\w[\w &/+-]*\s*:\s*")  # e.g., "Languages: Python, ..."
_TITLE_CASE = re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$")  # "Technical Skills"


# --------------- Public API ---------------
def parse_pdf_resume(file_bytes: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    PDF → text → contact + skills (from 'Skills' section).
    """
    try:
        import fitz  # PyMuPDF
    except Exception as e:
        raise ParseError("Missing dependency: pymupdf (pip install pymupdf)") from e

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise EncryptedOrCorruptPDF("PDF is encrypted or corrupt; cannot be opened.") from e

    try:
        pages = []
        for page in doc:
            pages.append(page.get_text("text"))
        raw_text = "\n\n".join(pages)
        page_count = doc.page_count
    finally:
        doc.close()

    text = _normalize_text(raw_text)
    if not text.strip():
        raise EmptyTextError("No extractable text found (likely a scanned PDF).")

    # Contact (fast + forgiving)
    contact = _extract_contact(text)

    # Skills (find the skills block → split by commas and newlines → strip any 'Category:' prefixes)
    skills = _extract_skills(text)

    meta = {
        "kind": "pdf",
        "filename": filename,
        "pages": page_count,
        "chars": len(text),
        "words": len(text.split()),
    }

    return {"text": text, "contact": contact, "skills": skills, "meta": meta}

# --------------- Normalization ---------------
def _normalize_text(text: str) -> str:
    if not text:
        return ""
    for k, v in LIGS.items():
        text = text.replace(k, v)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = CTRL_RE.sub("", text)
    # Collapse spaces/tabs per line but preserve line breaks
    lines = [WS_RE.sub(" ", ln).strip() for ln in text.split("\n")]
    return "\n".join(lines).strip()

# --------------- Contact (only what we need) ---------------
def _extract_contact(text: str) -> Dict[str, Optional[str]]:
    # Name guess: first non-contact-ish line within first ~20 lines
    header = "\n".join(text.split("\n")[:20])
    name = _guess_name(header)

    emails = EMAIL_RE.findall(text)
    phones = PHONE_RE.findall(text)

    linkedin = None
    github = None
    for line in text.splitlines():
        m_li = LINKEDIN_LINE_RE.search(line)
        if m_li and not linkedin:
            linkedin = _clean_url(m_li.group(0))
        m_gh = GITHUB_LINE_RE.search(line)
        if m_gh and not github:
            github = _clean_url(m_gh.group(0))
        if linkedin and github:
            break

    return {
        "name": name,
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "linkedin": linkedin,
        "github": github,
    }

def _guess_name(block: str) -> Optional[str]:
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    for ln in lines:
        low = ln.lower()
        if "@" in ln or "linkedin" in low or "github" in low or low.startswith(("email","phone","tel","portfolio")):
            continue
        if 1 <= len(ln.split()) <= 6:
            return ln
    return None

def _clean_url(u: str) -> str:
    u = u.strip().strip(').,;:!?"\'')
    if not u.startswith("http"):
        u = "https://" + u
    return u

# --------------- Skills (just from the Skills section) ---------------
def _extract_skills(text: str) -> List[str]:
    """
    Find a 'Skills' or 'Technical Skills' section (case-insensitive),
    capture its block, then split tokens:
      - primarily commas,
      - also newlines (if listed vertically),
      - if a token contains a colon, drop everything up to and including ':'.
    """
    block = _find_skills_block(text)
    if not block:
        return []

    chunks: List[str] = []
    # First split by commas, then split each piece by newline
    for part in block.split(","):
        for sub in part.split("\n"):
            token = sub.strip()
            if not token:
                continue
            if ":" in token:                 # drop category labels like "Languages: Python"
                token = token.split(":", 1)[1].strip()
            token = token.lower()
            if len(token) > 1:
                chunks.append(token)

    # De-duplicate while preserving order
    seen, out = set(), []
    for s in chunks:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out

def _find_skills_block(text: str) -> Optional[str]:
    """
    Locate the Skills section by scoring lines for 'header-ness' (contains 'skill',
    short, header-ish casing, separated by blanks, etc.). Then collect the lines
    that follow until a new header/double blank/hard cap.
    """
    lines = text.split("\n")

    header_idx = None
    best_score = -999
    for i in range(len(lines)):
        is_hdr, sc = _score_skills_header_line(lines, i)
        if is_hdr and sc > best_score:
            header_idx, best_score = i, sc
            break  # first good header wins (earliest 'Skills' on the page)

    if header_idx is None:
        return None

    # collect block after header
    block_lines: list[str] = []
    blanks_in_a_row = 0
    HARD_CAP = 40  # keep sections bounded even in odd layouts

    for j in range(header_idx + 1, min(len(lines), header_idx + 1 + HARD_CAP)):
        ln = lines[j]
        if not (ln or "").strip():
            blanks_in_a_row += 1
            if blanks_in_a_row >= 2:
                break
            block_lines.append("")  # keep a single blank
            continue
        blanks_in_a_row = 0

        # stop if we see another header-ish line (but allow category lines inside Skills)
        if _looks_like_header(ln) and not _CATEGORY_LINE.match(ln):
            break

        block_lines.append(ln)

    block = "\n".join(block_lines).strip()
    return block or None
    """
    Grab the text right after a line that looks like a Skills header
    until the next ALL-CAPS-ish header or a large blank gap.
    """
    lines = text.split("\n")
    header_idx = None
    skills_hdr = re.compile(r"^\s*(technical\s+skills|skills)\s*:?\s*$", re.IGNORECASE)

    for i, ln in enumerate(lines):
        if skills_hdr.match(ln):
            header_idx = i
            break

    if header_idx is None:
        return None

    # Collect lines after the header until another header-ish line or big gap
    block_lines: List[str] = []
    for ln in lines[header_idx+1:]:
        if not ln.strip():
            # stop if we hit a double blank (paragraph break)
            if block_lines and block_lines[-1] == "":
                break
            block_lines.append("")  # keep a single blank as separator
            continue
        # New header if the line is short and looks like a section title
        if _looks_like_header(ln):
            break
        block_lines.append(ln)

    # Join back; caller will split
    return "\n".join(block_lines).strip()

def _looks_like_header(line: str) -> bool:
    s = line.strip()
    if len(s) > 60:
        return False
    # Many resumes use Title Case or ALL CAPS for headers, often without punctuation
    return s.isupper() or re.match(r"^[A-Z][A-Za-z ]{2,}$", s) is not None

def _score_skills_header_line(lines: list[str], i: int) -> tuple[bool, int]:
    """
    Return (is_header, score) for lines[i].
    Uses only text heuristics:
      + contains 'skill' as a whole word
      + short length (<= 40) and few tokens (<= 6)
      + header-ish casing (ALL CAPS or Title Case)
      + separated by blank line before/after
      - starts with bullet
      - looks like a category line 'X: ...'
      - ends like a sentence
    Accept if score >= 3.
    """
    s = (lines[i] or "").strip()
    if not s:
        return (False, 0)

    # must contain 'skill' as whole word somewhere
    if not _SKILLS_WORD.search(s):
        return (False, 0)

    score = 0

    # positives
    if len(s) <= 40:
        score += 1
    if len(_WORD.findall(s)) <= 6:
        score += 1
    if s.isupper() or _TITLE_CASE.match(s):
        score += 2

    prev_blank = (i > 0 and not (lines[i-1] or "").strip())
    next_blank = (i+1 < len(lines) and not (lines[i+1] or "").strip())
    if prev_blank:
        score += 1
    if next_blank:
        score += 1

    # negatives
    if s.startswith(BULLET_MARKERS):
        score -= 3
    if _CATEGORY_LINE.match(s):  # "Languages: ..." is not a header, it's inside Skills
        score -= 2
    if s.endswith((".", "!", "?")):
        score -= 2
    if s.count(",") >= 2 or len(s) > 60:
        score -= 1

    return (score >= 3, score)

