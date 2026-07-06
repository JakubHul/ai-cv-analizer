from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "CV Analyzer AI"
    database_path: str = os.getenv("DATABASE_PATH", "app/db/cv_analyzer.db")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")


settings = Settings()
