"""Response schemas for health check endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    mode: str
    commit: str


class DBHealthResponse(BaseModel):
    status: str
    latency_ms: float
    migration_head: str | None = None
