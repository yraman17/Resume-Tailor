# matcher.py
from __future__ import annotations
import re
from typing import List, Dict

# --- helpers ---------------------------------------------------

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()

def _canon_list(items: List[str]) -> List[str]:
    out, seen = [], set()
    for x in items or []:
        t = _normalize(x)
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out

# --- core API --------------------------------------------------

def classify_and_score(keywords: List[str],
                       resume_skills: List[str],
                       resume_text: str) -> Dict:
    """
    Compare JD `keywords` against resume `skills` and `text`.

    Returns:
    {
      "in_skills": [...],
      "in_text_not_skills": [...],
      "missing": [...],
      "suggest_add_to_skills": [...],
      "scores": {"coverage": float, "overall": float},  # percentages 0–100
      "meta": {"num_keywords": int, "resume_chars": int}
    }
    """
    kws = _canon_list(keywords)
    skills = set(_canon_list(resume_skills))
    text_lc = _normalize(resume_text or "")

    in_skills = []
    in_text_not_skills = []
    missing = []

    for k in kws:
        if k in skills:
            in_skills.append(k)
        elif k and k in text_lc:
            in_text_not_skills.append(k)
        else:
            missing.append(k)

    # score: fraction of keywords present anywhere (skills OR text)
    matched = len(in_skills) + len(in_text_not_skills)
    total = len(kws) if kws else 1
    coverage_ratio = matched / total

    # convert to percentage
    coverage_pct = round(coverage_ratio * 100, 2)
    overall_pct = coverage_pct  # same for MVP

    return {
      "in_skills": in_skills,
      "in_text_not_skills": in_text_not_skills,
      "missing": missing,
      "suggest_add_to_skills": in_text_not_skills,  # present in text but not listed in Skills
      "scores": {
        "coverage": coverage_pct,  # now percent
        "overall": overall_pct,    # now percent
      },
      "meta": {
        "num_keywords": len(kws),
        "resume_chars": len(text_lc),
      }
    }
