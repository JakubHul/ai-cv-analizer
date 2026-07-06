from dataclasses import dataclass


@dataclass
class AnalysisRecord:
    id: str
    created_at: str
    updated_at: str
    cv_filename: str
    job_title: str | None
    company: str | None
    job_description_raw: str
    cv_text_clean: str
    score: int
    summary: str
