import os
import sqlite3

from app.core.config import settings


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)

    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                cv_filename TEXT NOT NULL,
                job_title TEXT,
                company TEXT,
                job_description_raw TEXT NOT NULL,
                cv_text_clean TEXT NOT NULL,
                score INTEGER NOT NULL,
                summary TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS analysis_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT NOT NULL,
                skill TEXT NOT NULL,
                skill_type TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            );

            CREATE TABLE IF NOT EXISTS missing_skill_explanations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT NOT NULL,
                skill TEXT NOT NULL,
                reason TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            );

            CREATE TABLE IF NOT EXISTS analysis_meta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            );

            CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at);
            CREATE INDEX IF NOT EXISTS idx_analysis_skills_analysis_id ON analysis_skills(analysis_id);
            CREATE INDEX IF NOT EXISTS idx_missing_skill_explanations_analysis_id ON missing_skill_explanations(analysis_id);
            CREATE INDEX IF NOT EXISTS idx_recommendations_analysis_id ON recommendations(analysis_id);
            """
        )
