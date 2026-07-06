from dataclasses import dataclass


@dataclass
class MatchResult:
    score: int
    matched_skills: list[str]
    missing_skills: list[str]


@dataclass
class MissingSkillExplanation:
    skill: str
    reason: str


@dataclass
class AnalysisOutput:
    analysis_id: str
    score: int
    matched_skills: list[str]
    missing_skills: list[str]
    missing_skill_explanations: list[MissingSkillExplanation]
    summary: str
    recommendations: list[str]
    strengths: list[str]
    created_at: str
