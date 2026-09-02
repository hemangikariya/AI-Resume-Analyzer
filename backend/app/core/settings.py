import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Resume Analyzer"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Security
    JWT_SECRET: str = "your-secure-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_URL: str = "sqlite:///./resume_analyzer.db"

    # LLM Settings
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "gemini-1.5-flash"

    # Storage Locations
    UPLOAD_DIR: str = "./storage"
    LOG_FILE: str = "./logs/backend.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def resumes_dir(self) -> Path:
        p = Path(self.UPLOAD_DIR) / "resumes"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def reports_dir(self) -> Path:
        p = Path(self.UPLOAD_DIR) / "reports"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def temp_dir(self) -> Path:
        p = Path(self.UPLOAD_DIR) / "temp"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def logs_dir(self) -> Path:
        p = Path(self.LOG_FILE).parent
        p.mkdir(parents=True, exist_ok=True)
        return p

settings = Settings()
