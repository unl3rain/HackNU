from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "SmartBot API"
    API_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
    ]

    DATABASE_URL: str = "sqlite:///./smartbot.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET: str = "devsecret"  
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 10

    STORAGE_PROVIDER: str = "local"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_S3_BUCKET: str | None = None
    AWS_REGION: str | None = None

    GEMINI_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None
    LLM_PROVIDER: str = "gemini"  
    LLM_MODEL: str | None = None  
    class Config:
        env_file = ".env"


settings = Settings()
