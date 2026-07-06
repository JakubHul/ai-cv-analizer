from app.core.database import get_connection


class AnalysisRepository:
    def save_analysis(
        self,
        analysis_id: str,
        created_at: str,
        cv_filename: str,
        job_description_raw: str,
        cv_text_clean: str,
        score: int,
        summary: str,
        matched_skills: list[str],
        missing_skills: list[str],
        cv_skills: list[str],
        job_skills: list[str],
        explanations: list[dict],
        recommendations: list[str],
        strengths: list[str],
        job_title: str | None = None,
        company: str | None = None,
    ) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO analyses (
                    id, created_at, updated_at, cv_filename, job_title, company,
                    job_description_raw, cv_text_clean, score, summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    created_at,
                    created_at,
                    cv_filename,
                    job_title,
                    company,
                    job_description_raw,
                    cv_text_clean,
                    score,
                    summary,
                ),
            )

            for skill in cv_skills:
                conn.execute(
                    "INSERT INTO analysis_skills (analysis_id, skill, skill_type) VALUES (?, ?, ?)",
                    (analysis_id, skill, "cv"),
                )

            for skill in job_skills:
                conn.execute(
                    "INSERT INTO analysis_skills (analysis_id, skill, skill_type) VALUES (?, ?, ?)",
                    (analysis_id, skill, "required"),
                )

            for skill in matched_skills:
                conn.execute(
                    "INSERT INTO analysis_skills (analysis_id, skill, skill_type) VALUES (?, ?, ?)",
                    (analysis_id, skill, "matched"),
                )

            for skill in missing_skills:
                conn.execute(
                    "INSERT INTO analysis_skills (analysis_id, skill, skill_type) VALUES (?, ?, ?)",
                    (analysis_id, skill, "missing"),
                )

            for item in explanations:
                conn.execute(
                    "INSERT INTO missing_skill_explanations (analysis_id, skill, reason) VALUES (?, ?, ?)",
                    (analysis_id, item.get("skill", ""), item.get("reason", "")),
                )

            for idx, rec in enumerate(recommendations):
                conn.execute(
                    "INSERT INTO recommendations (analysis_id, position, text) VALUES (?, ?, ?)",
                    (analysis_id, idx, rec),
                )

            for idx, strength in enumerate(strengths):
                conn.execute(
                    "INSERT INTO analysis_meta (analysis_id, key, value) VALUES (?, ?, ?)",
                    (analysis_id, f"strength_{idx}", strength),
                )

    def get_analysis(self, analysis_id: str) -> dict | None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM analyses WHERE id = ?",
                (analysis_id,),
            ).fetchone()
            if not row:
                return None

            skills_rows = conn.execute(
                "SELECT skill, skill_type FROM analysis_skills WHERE analysis_id = ?",
                (analysis_id,),
            ).fetchall()
            explanation_rows = conn.execute(
                "SELECT skill, reason FROM missing_skill_explanations WHERE analysis_id = ?",
                (analysis_id,),
            ).fetchall()
            recommendation_rows = conn.execute(
                "SELECT text FROM recommendations WHERE analysis_id = ? ORDER BY position ASC",
                (analysis_id,),
            ).fetchall()
            strengths_rows = conn.execute(
                "SELECT value FROM analysis_meta WHERE analysis_id = ? AND key LIKE 'strength_%' ORDER BY key ASC",
                (analysis_id,),
            ).fetchall()

        payload = dict(row)
        payload["skills"] = [dict(item) for item in skills_rows]
        payload["missing_skill_explanations"] = [dict(item) for item in explanation_rows]
        payload["recommendations"] = [item["text"] for item in recommendation_rows]
        payload["strengths"] = [item["value"] for item in strengths_rows]
        return payload
