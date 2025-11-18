"""Application settings management using Pydantic."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # LLM Provider Configuration
    llm_provider: str = Field(default="ollama", description="LLM provider to use")
    llm_model: str = Field(default="llama3.1:8b", description="Model name")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # Cloud Provider API Keys
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None

    # Local LLM Configuration
    ollama_base_url: str = Field(default="http://localhost:11434")
    lmstudio_base_url: str = Field(default="http://localhost:1234/v1")

    # Database Configuration
    postgres_url: str = Field(
        default="postgresql://admin:password@localhost:5432/guardianeye"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")
    chroma_persist_directory: str = Field(default="./data/chroma")

    # Application Configuration
    app_env: str = Field(default="development")
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1, le=65535)
    log_level: str = Field(default="INFO")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )

    # Security
    jwt_secret_key: str = Field(default="change-this-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)

    # Monitoring (Optional)
    langsmith_api_key: str | None = None
    langsmith_project: str = Field(default="guardianeye")
    langsmith_tracing: bool = Field(default=False)

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"


# Global settings instance
settings = Settings()
