from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Application
    APP_NAME: str = "ChatterMate Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./chatbot.db"

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # AI Settings
    DEFAULT_AI_PROVIDER: str = "openai"
    DEFAULT_MODEL: str = "gpt-4-turbo-preview"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
