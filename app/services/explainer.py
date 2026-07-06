import json
from urllib import error, request

from app.core.config import settings
from app.core.errors import LocalModelUnavailableError


def _extract_json(payload: str) -> dict:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        start = payload.find("{")
        end = payload.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("AI response is not valid JSON.")
        return json.loads(payload[start : end + 1])


def _call_ollama(prompt: str) -> str:
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
        with request.urlopen(req, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise LocalModelUnavailableError(
            "Local AI model is not available. Start Ollama and run: ollama run llama3"
        ) from exc

    response_text = str(data.get("response", "")).strip()
    if not response_text:
        raise ValueError("Local AI returned an empty response.")
    return response_text


def build_explanations(
    missing_skills: list[str],
    matched_skills: list[str],
    score: int,
    job_description: str,
) -> tuple[list[dict], str, list[str], list[str]]:
    """Generate explainability text only. Score/matching remain deterministic and untouched."""
    if not missing_skills:
        return [], "Candidate matches all required skills.", ["Strong skills overlap"], []

    prompt = (
        "You are an ATS explainability assistant.\n"
        "Do not calculate or change score. Score is fixed and deterministic.\n"
        "Return ONLY JSON with keys: explanations, summary, recommendations, strengths.\n"
        "- explanations: list of {skill, reason} for each missing skill\n"
        "- reason format should be market-style statement, e.g. 'Required in 7/10 similar job descriptions'\n"
        "- summary: 2-3 sentences\n"
        "- recommendations: 3-6 actionable items\n"
        "- strengths: 2-6 concise points based on matched skills\n\n"
        f"Fixed score: {score}\n"
        f"Matched skills: {matched_skills}\n"
        f"Missing skills: {missing_skills}\n"
        f"Job description: {job_description}\n"
    )

    data = _extract_json(_call_ollama(prompt))
    explanations = data.get("explanations", [])
    summary = str(data.get("summary", "")).strip() or "Profile has partial alignment with job requirements."
    recommendations = [str(x) for x in data.get("recommendations", [])]
    strengths = [str(x) for x in data.get("strengths", [])]

    normalized_explanations: list[dict] = []
    explanation_map = {
        str(item.get("skill", "")).strip(): str(item.get("reason", "")).strip()
        for item in explanations
        if isinstance(item, dict)
    }
    for skill in missing_skills:
        reason = explanation_map.get(skill) or "Required in similar job descriptions for this role."
        normalized_explanations.append({"skill": skill, "reason": reason})

    return normalized_explanations, summary, recommendations, strengths
