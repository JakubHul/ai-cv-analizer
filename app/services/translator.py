import re

from app.core.constants import SKILL_SYNONYMS


def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace — used for text comparison."""
    lowered = text.lower()
    cleaned = re.sub(r"\s+", " ", lowered)
    return cleaned.strip()


def normalize_skills(skills: list[str]) -> list[str]:
    """
    Normalise a list of extracted skill strings to their canonical forms.

    For each skill:
      1. Lowercase + collapse whitespace (normalize_text)
      2. Look up in SKILL_SYNONYMS (longest-key-first to avoid partial matches)
         If found → replace with canonical value
         If not found → keep the normalised string as-is

    Returns a sorted, deduplicated list.

    Note: SKILL_SYNONYMS keys are sorted by descending length so that
    multi-word phrases (e.g. 'full uk driving licence') are resolved before
    their sub-phrases (e.g. 'driving licence').
    """
    # Build a sorted synonym lookup once (longest key first)
    sorted_synonyms = sorted(SKILL_SYNONYMS.keys(), key=len, reverse=True)

    canonical: set[str] = set()
    for skill in skills:
        key = normalize_text(skill)
        resolved: str | None = None

        # Try exact lookup first
        if key in SKILL_SYNONYMS:
            resolved = SKILL_SYNONYMS[key]
        else:
            # Try longest-match substring: check if any synonym key appears
            # as a whole-word match inside the skill string
            for syn_key in sorted_synonyms:
                pattern = rf"(^|\W){re.escape(syn_key)}($|\W)"
                if re.search(pattern, key):
                    resolved = SKILL_SYNONYMS[syn_key]
                    break

        canonical_skill = resolved if resolved else key
        if canonical_skill:
            canonical.add(canonical_skill)

    return sorted(canonical)
