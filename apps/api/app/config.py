"""Application configuration — all settings read from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.enums import AppMode


class Settings(BaseSettings):
    """
    Platform configuration loaded from environment variables.

    See .env.example for all variables and their defaults.
    NEVER hardcode secrets here — use environment variables or Vault.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ---------------------------------------------------------------------------
    # Database
    # ---------------------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://bsm:bsm@localhost:5432/bsm",
        description="SQLAlchemy async database URL",
    )
    database_pool_size: int = Field(default=20, ge=1, le=100)
    database_max_overflow: int = Field(default=10, ge=0, le=50)

    # ---------------------------------------------------------------------------
    # Application
    # ---------------------------------------------------------------------------
    app_mode: AppMode = AppMode.LOCAL
    debug: bool = False
    secret_key: str = Field(
        default="CHANGE-ME-IN-PRODUCTION",
        description="32-byte random secret used for signing",
    )
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="CORS allowed origins",
    )

    # ---------------------------------------------------------------------------
    # Authentication (OIDC)
    # ---------------------------------------------------------------------------
    oidc_issuer: str = ""
    oidc_audience: str = "bsm-api"
    oidc_jwks_uri: str = ""

    # ---------------------------------------------------------------------------
    # Anthropic API
    # ---------------------------------------------------------------------------
    anthropic_api_key: str = ""
    # Model is pinned here. Changing this requires re-running the full eval suite.
    anthropic_model: str = "claude-sonnet-4-6"

    # Demo mode LLM key (separate billing, separate limits)
    demo_anthropic_api_key: str = ""
    demo_monthly_llm_budget_usd: float = 50.0

    # ---------------------------------------------------------------------------
    # Object storage (snapshots)
    # ---------------------------------------------------------------------------
    snapshot_storage_backend: str = "local"  # local | s3
    snapshot_local_path: str = "./data/snapshots"
    aws_region: str = "ap-south-1"
    s3_snapshot_bucket: str = ""

    # ---------------------------------------------------------------------------
    # Observability
    # ---------------------------------------------------------------------------
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "bsm-api"
    log_level: str = "INFO"

    @property
    def is_demo(self) -> bool:
        return self.app_mode == AppMode.DEMO

    @property
    def is_production(self) -> bool:
        return self.app_mode == AppMode.PRODUCTION


# Module-level singleton — import this in dependency injection
settings = Settings()
