"""
Platform HTTP middleware.

RequestIDMiddleware: assigns a UUID to every request, propagates it through
structlog context and returns it in the X-Request-ID response header.
"""

import uuid
from time import monotonic

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

REQUEST_ID_HEADER = "X-Request-ID"

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a unique request ID to every HTTP request.

    - Reads X-Request-ID from incoming headers (allows upstream trace propagation).
    - Generates a new UUID4 if the header is absent.
    - Binds the ID into the structlog context so every log line within the
      request handler automatically carries request_id=...
    - Logs method, path, status code, and latency after the response is sent.
    - Sets X-Request-ID on the response header.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: object) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = monotonic()
        response: Response = await call_next(request)  # type: ignore[operator]
        latency_ms = round((monotonic() - start) * 1000, 1)

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_ms=latency_ms,
        )

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
