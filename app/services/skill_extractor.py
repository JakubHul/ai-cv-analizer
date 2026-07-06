import json
import logging
import re
from urllib import error, request

from app.core.config import settings
from app.core.constants import (
    CANONICAL_SKILLS,
    EXPERIENCE_PATTERNS,
    ROLE_TO_SKILLS,
    SKILL_SYNONYMS,
)
from app.core.errors import LocalModelUnavailableError
from app.services.translator import normalize_text

_logger = logging.getLogger("ats.skill_extractor")


# ---------------------------------------------------------------------------
# Layer 1 — exact match against CANONICAL_SKILLS
# ---------------------------------------------------------------------------

def _extract_canonical(text: str) -> set[str]:
    """Find canonical skills that appear literally in the text."""
    normalized = normalize_text(text)
    found: set[str] = set()
    for skill in CANONICAL_SKILLS:
        pattern = rf"(^|\W){re.escape(skill.lower())}($|\W)"
        if re.search(pattern, normalized):
            found.add(skill)
    return found


# ---------------------------------------------------------------------------
# Layer 2 — synonym lookup (longest-match first)
# ---------------------------------------------------------------------------

def _extract_via_synonyms(text: str) -> set[str]:
    """
    Match SKILL_SYNONYMS keys against the text.
    Sorted by descending key length so multi-word phrases are matched before
    their sub-phrases (e.g. 'full uk driving licence' before 'driving licence').
    """
    normalized = normalize_text(text)
    found: set[str] = set()
    for synonym in sorted(SKILL_SYNONYMS.keys(), key=len, reverse=True):
        pattern = rf"(^|\W){re.escape(synonym)}($|\W)"
        if re.search(pattern, normalized):
            found.add(SKILL_SYNONYMS[synonym])
    return found


# ---------------------------------------------------------------------------
# Layer 3 — role-name expansion
# ---------------------------------------------------------------------------

def _extract_via_roles(text: str) -> set[str]:
    """
    Detect job-title / role mentions and expand them into implied skills.
    E.g. 'Plant Operator' -> ['plant operation', 'health and safety', 'construction labour']
    """
    normalized = normalize_text(text)
    found: set[str] = set()
    for role in sorted(ROLE_TO_SKILLS.keys(), key=len, reverse=True):
        pattern = rf"(^|\W){re.escape(role)}($|\W)"
        if re.search(pattern, normalized):
            found.update(ROLE_TO_SKILLS[role])
    return found


# ---------------------------------------------------------------------------
# Layer 4 — experience-pattern regex
# ---------------------------------------------------------------------------

def _extract_via_patterns(text: str) -> set[str]:
    """
    Apply EXPERIENCE_PATTERNS regexes to catch descriptive phrases.
    E.g. 'Assisted Electricians'  -> 'electrical work support'
         'Worked at Heights'      -> 'working at heights'
         'CPCS Licence'           -> 'CPCS certification'
    """
    found: set[str] = set()
    for pattern, canonical_skill in EXPERIENCE_PATTERNS:
        if pattern.search(text):
            found.add(canonical_skill)
    return found


# ---------------------------------------------------------------------------
# Deterministic extractor — combines all 4 layers
# ---------------------------------------------------------------------------

def _extract_skills_deterministic(text: str) -> list[str]:
    """
    Multi-layer deterministic skill extraction.

    Layer 1 — exact match in CANONICAL_SKILLS
    Layer 2 — synonym lookup in SKILL_SYNONYMS
    Layer 3 — role-name expansion via ROLE_TO_SKILLS
    Layer 4 — regex patterns via EXPERIENCE_PATTERNS

    Returns a sorted, deduplicated list of canonical skill strings.
    """
    found: set[str] = set()
    found |= _extract_canonical(text)
    found |= _extract_via_synonyms(text)
    found |= _extract_via_roles(text)
    found |= _extract_via_patterns(text)
    return sorted(found)


# ---------------------------------------------------------------------------
# Ollama Layer 5 — role/domain detection ONLY (no skill lists, no scoring)
# ---------------------------------------------------------------------------

def _detect_role_via_ollama(text: str) -> dict:
    """
    Use Ollama ONLY to detect the job role / domain of the text.

    CONTRACT:
      - Returns: {"role": "<role>", "domain": "<domain>", "context_summary": "<one sentence>"}
      - Does NOT return skill lists.
      - Does NOT generate synonyms.
      - Does NOT influence score directly.
      - The returned role is looked up in ROLE_TO_SKILLS (deterministic mapping).

    If Ollama is unavailable, raises LocalModelUnavailableError.
    """
    prompt = (
        "Identify the primary job role and industry domain of the following text.\n"
        "Return ONLY a JSON object with exactly these keys:\n"
        "  'role': the main job role in English, lowercase "
        "(e.g. 'mechanic', 'construction worker', 'software developer', 'warehouse operative')\n"
        "  'domain': the industry domain in English, lowercase "
        "(e.g. 'automotive', 'construction', 'it', 'warehouse', 'retail', 'manufacturing')\n"
        "  'context_summary': one short sentence describing the text in English\n"
        "IMPORTANT: Do NOT list skills. Do NOT generate competencies. "
        "Only identify the role and domain.\n\n"
        f"Text:\n{text[:1500]}\n"
    )
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }
    req = request.Request(
        settings.ollama_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise LocalModelUnavailableError(
            "Local AI model is not available. Start Ollama and run: ollama run llama3"
        ) from exc

    response_text = str(data.get("response", "")).strip()
    if not response_text:
        return {}

    try:
        return json.loads(response_text)
    except (json.JSONDecodeError, AttributeError):
        return {}


def _skills_from_ollama_role(text: str) -> list[str]:
    """
    Layer 5: Ask Ollama for the role, then map it deterministically to skills.

    Flow:
      text → Ollama (role detection only) → role string
           → ROLE_TO_SKILLS lookup (deterministic) → canonical skills

    Ollama output does NOT affect score. Score is always deterministic.
    """
    try:
        role_info = _detect_role_via_ollama(text)
    except LocalModelUnavailableError:
        _logger.debug("[ATS] Ollama unavailable — skipping role detection")
        return []

    role = str(role_info.get("role", "")).strip().lower()
    domain = str(role_info.get("domain", "")).strip().lower()
    summary = str(role_info.get("context_summary", "")).strip()

    _logger.debug("[ATS] Ollama detected role='%s' domain='%s' summary='%s'",
                  role, domain, summary)

    # Look up role in ROLE_TO_SKILLS (deterministic — no AI influence on skills)
    skills: set[str] = set()

    if role and role in ROLE_TO_SKILLS:
        skills.update(ROLE_TO_SKILLS[role])
        _logger.debug("[ATS] Role '%s' mapped to skills: %s", role, ROLE_TO_SKILLS[role])

    # Also try domain as a role key (e.g. domain="automotive" → not in dict, but
    # domain="mechanic" might be if user phrased it that way)
    if domain and domain in ROLE_TO_SKILLS and domain != role:
        skills.update(ROLE_TO_SKILLS[domain])
        _logger.debug("[ATS] Domain '%s' mapped to skills: %s", domain, ROLE_TO_SKILLS[domain])

    return sorted(skills)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_skills(text: str) -> list[str]:
    """
    Extract skills from text using a 5-layer pipeline.

    Layers 1-4 are fully deterministic (no AI):
      Layer 1 — exact match in CANONICAL_SKILLS
      Layer 2 — synonym lookup in SKILL_SYNONYMS (longest-match first)
      Layer 3 — role-name expansion via ROLE_TO_SKILLS
      Layer 4 — regex patterns via EXPERIENCE_PATTERNS

    Layer 5 (fallback, only when layers 1-4 return nothing):
      Ollama detects the job ROLE only → role is mapped to skills via
      ROLE_TO_SKILLS (deterministic). Ollama does NOT generate skill lists,
      does NOT generate synonyms, does NOT influence the score.

    Score is NEVER computed here — this function only extracts skills.
    """
    _logger.debug("[ATS] extract_skills called, text length=%d", len(text))

    # Layers 1-4: deterministic
    layer1 = _extract_canonical(text)
    layer2 = _extract_via_synonyms(text)
    layer3 = _extract_via_roles(text)
    layer4 = _extract_via_patterns(text)

    deterministic = sorted(layer1 | layer2 | layer3 | layer4)

    _logger.debug("[ATS] Layer1 (canonical):  %s", sorted(layer1))
    _logger.debug("[ATS] Layer2 (synonyms):   %s", sorted(layer2))
    _logger.debug("[ATS] Layer3 (roles):      %s", sorted(layer3))
    _logger.debug("[ATS] Layer4 (patterns):   %s", sorted(layer4))
    _logger.debug("[ATS] Deterministic total: %s", deterministic)

    if deterministic:
        return deterministic

    # Layer 5: Ollama role detection → deterministic skill mapping
    _logger.debug("[ATS] Deterministic layers returned nothing — trying Ollama role detection")
    ollama_skills = _skills_from_ollama_role(text)
    _logger.debug("[ATS] Layer5 (ollama role→skills): %s", ollama_skills)
    return ollama_skills
