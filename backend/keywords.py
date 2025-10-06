# keywords.py
from __future__ import annotations
import re
from typing import List, Dict, Optional, Tuple

# Keep techy tokens like c++, c#, .net, node.js, react-dom, ci/cd
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9\+\#\.\-\/]{0,}")

# Map common variants to canonical forms
ALIASES = {
    "node.js": "node", "nodejs": "node",
    "react.js": "react", "reactjs": "react",
    "postgresql": "postgres", "postgre": "postgres",
    "k8s": "kubernetes",
    "ci/cd": "ci-cd",
    "c plus plus": "c++", "c sharp": "c#",
    ".net": "dotnet",
    "rest api": "rest",
    "js": "javascript", "ts": "typescript",
}

# Whitelist of tech words we care about (expand anytime)
TECH_SET = {
    "python","javascript","typescript","react","node","express","fastapi","django","flask",
    "aws","gcp","azure","docker","kubernetes","k8s","terraform","ansible","ci-cd",
    "sql","postgres","mysql","mongodb","redis","graphql","rest",
    "java","spring","kotlin","go","golang","rust","php","ruby","dotnet","c","c++","c#",
    "pandas","numpy","pytorch","tensorflow","scikit-learn","sklearn","spark","airflow","dbt",
    "excel","tableau", "backend", "frontend", "full-stack"
}

# Phrases we want to keep intact if present
PHRASES = [
    "machine learning","data science","data engineering","computer vision",
    "rest api","continuous integration","continuous delivery","continuous deployment", "full stack"
]

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()

# Strip only leading/trailing punctuation; keep internal . + # / (node.js, c++, ci/cd)
def _clean_token(t: str) -> str:
    if not t: return ""
    t = t.strip().lower()
    t = t.strip('.,;:!?)”’"\\]}>')  # trailing
    t = t.lstrip('([<{“‘"')         # leading
    return t

def _apply_alias(t: str) -> str:
    return ALIASES.get(t, t)

def _is_techy(tok: str) -> bool:
    # Keep clear tech items; restrict slashes to known patterns
    if tok in TECH_SET:
        return True
    if tok in {"ci/cd", "rest/api", "graphql/api"}:
        return True
    if any(ch in tok for ch in [".","+","#"]) and len(tok) > 1:
        return True
    if tok.endswith(("sql","api","db")):
        return True
    return False


def _extract_phrases(text: str) -> List[str]:
    hits = []
    for p in PHRASES:
        if p in text:
            hits.append(_apply_alias(p))
    return hits

def extract_keywords(job_text: str, max_k: int = 20,
                     custom_keywords: Optional[List[str]] = None) -> List[str]:
    """
    Return a simple ordered list of core JD keywords (strings), length <= max_k.
    - Tokenize JD
    - Clean + alias common variants
    - Keep only techy terms (whitelist + safe heuristics)
    - Rank by frequency, then alphabetically as tie-breaker
    - Include phrases and (optionally) user-specified custom keywords
    """
    txt = _normalize(job_text)
    if not txt:
        return []

    # Phrases first (ensures we keep them as a unit once if present)
    phrase_hits = set(_extract_phrases(txt))

    # Tokenize
    raw = [t for t in TOKEN_RE.findall(txt) if t]
    toks: List[str] = []
    for t in raw:
        t = _apply_alias(_clean_token(t))
        if len(t) <= 1:
            continue
        if not _is_techy(t):
            continue
        toks.append(t)

    # Frequency count
    freqs: Dict[str,int] = {}
    for t in toks:
        freqs[t] = freqs.get(t, 0) + 1
    for p in phrase_hits:
        freqs[p] = max(freqs.get(p, 0), 1)

    # Include custom keywords (force-in, even if not in TECH_SET)
    if custom_keywords:
        for ck in custom_keywords:
            k = _apply_alias(_clean_token(_normalize(ck)))
            if not k:
                continue
            freqs[k] = max(freqs.get(k, 0), 1)

    # Rank by (frequency desc, then token asc) and trim
    ranked = sorted(freqs.items(), key=lambda kv: (-kv[1], kv[0]))
    result = [tok for tok, _ in ranked][:max_k]

    return result
