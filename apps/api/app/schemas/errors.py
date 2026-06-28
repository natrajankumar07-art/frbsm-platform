"""Standard error envelope schemas returned by all error handlers."""

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    code: str | None = None


class ErrorEnvelope(BaseModel):
    code: str
    message: str
    request_id: str | None = None
    details: list[ErrorDetail] | None = None
