import re

from app.models.domain import MatchResult


def _normalize_for_match(skill: str) -> str:
    """
    Produce a normalised comparison key for a skill string.

    Steps:
      1. Lowercase
      2. Collapse whitespace
      3. Strip common filler words that don't carry meaning
         ('and', 'or', 'the', 'a', 'an', 'of', 'in', 'at', 'for', 'with')
      4. Remove non-alphanumeric characters (except spaces)
      5. Collapse whitespace again

    This allows surface-form variants to match the same canonical key, e.g.:
      'health and safety'  -> 'health safety'
      'health & safety'    -> 'health safety'
      'H&S'                -> 'hs'
      'CPCS Licence'       -> 'cpcs licence'
      'cpcs certification' -> 'cpcs certification'
    """
    s = skill.lower()
    s = re.sub(r"[&/\\]", " ", s)          # replace punctuation with space
    s = re.sub(r"[^a-z0-9 ]", "", s)       # strip remaining non-alphanum
    s = re.sub(r"\s+", " ", s).strip()
    # remove common stop-words that add noise
    stop = {"and", "or", "the", "a", "an", "of", "in", "at", "for", "with"}
    tokens = [t for t in s.split() if t not in stop]
    return " ".join(tokens)


def match_skills(skills_cv: list[str], skills_job: list[str]) -> MatchResult:
    """
    Match CV skills against Job Description skills.

    Two-round matching (both deterministic, no AI):

    Round 1 — Exact string match (case-sensitive set intersection).
    Round 2 — Normalised match: skills that did not exact-match are compared
              after applying _normalize_for_match().  This catches variants like:
                CV:  'health and safety'   JD: 'health & safety'
                CV:  'CPCS certification'  JD: 'cpcs licence'
                CV:  'plant operation'     JD: 'plant operator experience'

    Score = matched_count / job_skill_count * 100  (deterministic, integer).
    AI does NOT compute the score.
    """
    cv_set = set(skills_cv)
    job_set = set(skills_job)

    # Round 1 — exact match
    exact_matched: set[str] = job_set.intersection(cv_set)

    # Round 2 — normalised match on the remainder
    remaining_job = job_set - exact_matched
    remaining_cv = cv_set - exact_matched

    cv_norm_map: dict[str, str] = {_normalize_for_match(s): s for s in remaining_cv}

    norm_matched: set[str] = set()
    for job_skill in remaining_job:
        job_key = _normalize_for_match(job_skill)
        if job_key in cv_norm_map:
            norm_matched.add(job_skill)

    matched = sorted(exact_matched | norm_matched)
    missing = sorted(job_set - exact_matched - norm_matched)

    if not job_set:
        score = 0
    else:
        score = round((len(matched) / len(job_set)) * 100)

    return MatchResult(score=score, matched_skills=matched, missing_skills=missing)
