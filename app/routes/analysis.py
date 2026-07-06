from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.errors import AppError
from app.models.api import AnalyzeResponse, MissingSkillExplanationResponse
from app.services.analysis_service import AnalysisService


router = APIRouter()
service = AnalysisService()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    cv_file: UploadFile = File(...),
    job_description: str = Form(...),
    job_title: str | None = Form(default=None),
    company: str | None = Form(default=None),
) -> AnalyzeResponse:
    try:
        result = await service.analyze(
            cv_file=cv_file,
            job_description=job_description,
            job_title=job_title,
            company=company,
        )
    except AppError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AnalyzeResponse(
        analysis_id=result.analysis_id,
        score=result.score,
        matched_skills=result.matched_skills,
        missing_skills=result.missing_skills,
        missing_skill_explanations=[
            MissingSkillExplanationResponse(skill=item.skill, reason=item.reason)
            for item in result.missing_skill_explanations
        ],
        strengths=result.strengths,
        summary=result.summary,
        recommendations=result.recommendations,
        created_at=result.created_at,
    )

