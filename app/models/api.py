from pydantic import BaseModel


class MissingSkillExplanationResponse(BaseModel):
    skill: str
    reason: str


class AnalyzeResponse(BaseModel):
    analysis_id: str
    score: int
    matched_skills: list[str]
    missing_skills: list[str]
    missing_skill_explanations: list[MissingSkillExplanationResponse]
    strengths: list[str]
    summary: str
    recommendations: list[str]
    created_at: str


class HealthResponse(BaseModel):
    status: str
    database: str
    ollama: str
