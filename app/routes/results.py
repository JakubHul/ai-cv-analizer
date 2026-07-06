from fastapi import APIRouter, HTTPException, status

from app.core.errors import AppError, NotFoundError
from app.models.api import AnalyzeResponse, MissingSkillExplanationResponse
from app.services.analysis_service import AnalysisService


router = APIRouter()
service = AnalysisService()


@router.get("/results/{analysis_id}", response_model=AnalyzeResponse)
async def get_result(analysis_id: str) -> AnalyzeResponse:
    try:
        result = service.get_result(analysis_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
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
