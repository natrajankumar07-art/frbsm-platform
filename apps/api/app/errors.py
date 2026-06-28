"""
Global exception handlers.

Registered on the FastAPI application in main.py. All handlers return the
standard ErrorEnvelope JSON shape so clients have a predictable error contract.
"""

import structlog
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .schemas.errors import ErrorDetail, ErrorEnvelope

logger = structlog.get_logger(__name__)


def _request_id(request: Request) -> str | None:
    return request.headers.get("X-Request-ID")


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    details = [
        ErrorDetail(
            field=".".join(str(loc) for loc in err["loc"]) if err.get("loc") else None,
            message=err["msg"],
            code=err.get("type"),
        )
        for err in exc.errors()
    ]
    body = ErrorEnvelope(
        code="VALIDATION_ERROR",
        message="Request validation failed.",
        request_id=_request_id(request),
        details=details,
    )
    logger.warning("request_validation_error", error_count=len(details))
    return JSONResponse(status_code=422, content=body.model_dump(exclude_none=True))


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    body = ErrorEnvelope(
        code="HTTP_ERROR",
        message=str(exc.detail),
        request_id=_request_id(request),
    )
    if exc.status_code >= 500:
        logger.error("http_exception", status_code=exc.status_code, detail=exc.detail)
    else:
        logger.info("http_exception", status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=body.model_dump(exclude_none=True),
        headers=getattr(exc, "headers", None),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = _request_id(request)
    logger.exception(
        "unhandled_exception",
        exc_type=type(exc).__name__,
    )
    body = ErrorEnvelope(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred. Use the request_id to locate logs.",
        request_id=request_id,
    )
    return JSONResponse(status_code=500, content=body.model_dump(exclude_none=True))
