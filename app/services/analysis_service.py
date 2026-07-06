import datetime as dt
import os
import tempfile
import uuid

from fastapi import UploadFile

from app.core.errors import NotFoundError, ValidationError
from app.models.domain import AnalysisOutput, MissingSkillExplanation
from app.repositories.analysis_repository import AnalysisRepository
from app.services.explainer import build_explanations
from app.services.matcher import match_skills
from app.services.pdf_parser import extract_text_from_pdf
from app.services.skill_extractor import extract_skills
from app.services.translator import normalize_skills


class AnalysisService:
    def __init__(self, repository: AnalysisRepository | None = None) -> None:
        self.repository = repository or AnalysisRepository()

    async def analyze(
        self,
        cv_file: UploadFile,
        job_description: str,
        job_title: str | None = None,
        company: str | None = None,
    ) -> AnalysisOutput:
        if not job_description.strip():
            raise ValidationError("Job description cannot be empty.")

        file_name = cv_file.filename or ""
        content_type = cv_file.content_type or ""
        if not file_name.lower().endswith(".pdf") or content_type not in {
            "application/pdf",
            "application/octet-stream",
        }:
            raise ValidationError("Uploaded file must be a PDF.")

        temp_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(await cv_file.read())
                temp_path = temp_file.name

            cv_text = extract_text_from_pdf(temp_path)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

        cv_skills = normalize_skills(extract_skills(cv_text))
        job_skills = normalize_skills(extract_skills(job_description))

        match_result = match_skills(skills_cv=cv_skills, skills_job=job_skills)

        explanations, summary, recommendations, strengths = build_explanations(
            missing_skills=match_result.missing_skills,
            matched_skills=match_result.matched_skills,
            score=match_result.score,
            job_description=job_description,
        )

        created_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        analysis_id = str(uuid.uuid4())

        self.repository.save_analysis(
            analysis_id=analysis_id,
            created_at=created_at,
            cv_filename=file_name,
            job_description_raw=job_description,
            cv_text_clean=cv_text,
            score=match_result.score,
            summary=summary,
            matched_skills=match_result.matched_skills,
            missing_skills=match_result.missing_skills,
            cv_skills=cv_skills,
            job_skills=job_skills,
            explanations=explanations,
            recommendations=recommendations,
            strengths=strengths,
            job_title=job_title,
            company=company,
        )

        return AnalysisOutput(
            analysis_id=analysis_id,
            score=match_result.score,
            matched_skills=match_result.matched_skills,
            missing_skills=match_result.missing_skills,
            missing_skill_explanations=[MissingSkillExplanation(**item) for item in explanations],
            summary=summary,
            recommendations=recommendations,
            strengths=strengths,
            created_at=created_at,
        )

    def get_result(self, analysis_id: str) -> AnalysisOutput:
        data = self.repository.get_analysis(analysis_id)
        if not data:
            raise NotFoundError("Analysis not found.")

        matched_skills = sorted(
            [item["skill"] for item in data["skills"] if item["skill_type"] == "matched"]
        )
        missing_skills = sorted(
            [item["skill"] for item in data["skills"] if item["skill_type"] == "missing"]
        )

        return AnalysisOutput(
            analysis_id=data["id"],
            score=int(data["score"]),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            missing_skill_explanations=[
                MissingSkillExplanation(skill=item["skill"], reason=item["reason"])
                for item in data["missing_skill_explanations"]
            ],
            summary=data["summary"],
            recommendations=data["recommendations"],
            strengths=data["strengths"],
            created_at=data["created_at"],
        )
