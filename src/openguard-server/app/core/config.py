from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "OpenGuard Kids Server"
    API_V1_STR: str = "/api/v1"

    # Security & JWT
    SECRET_KEY: str = "changethis-in-production-openguardkids-secret-key-32bytes"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Cho Device token
    SESSION_COOKIE_MAX_AGE: int = 12 * 3600  # 12 giờ cho Web Session (NIST SP 800-63B)
    SESSION_COOKIE_NAME: str = "ogk_session"

    # CORS configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Database
    DATABASE_URL: str = "sqlite:///./data/ogk_server.db"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
