import logging
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("croclens.api")


class SecurityHeadersAndRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit_per_minute: int) -> None:
        super().__init__(app)
        self.rate_limit_per_minute = rate_limit_per_minute
        self._request_times: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        client_key = request.client.host if request.client else "unknown"

        if self._is_rate_limited(client_key):
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please wait briefly before trying again.",
                    "request_id": request_id,
                },
            )
        else:
            started_at = time.perf_counter()
            try:
                response = await call_next(request)
            except Exception:
                logger.exception("Unhandled API error", extra={"request_id": request_id, "path": request.url.path})
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "detail": "CrocLens hit an unexpected error. No internal details were exposed.",
                        "request_id": request_id,
                    },
                )
            elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "elapsed_ms": elapsed_ms,
                },
            )

        _add_security_headers(response, request_id)
        return response

    def _is_rate_limited(self, client_key: str) -> bool:
        if self.rate_limit_per_minute <= 0:
            return False

        now = time.monotonic()
        window_start = now - 60
        request_times = self._request_times[client_key]

        while request_times and request_times[0] < window_start:
            request_times.popleft()

        if len(request_times) >= self.rate_limit_per_minute:
            return True

        request_times.append(now)
        return False


def _add_security_headers(response: Response, request_id: str) -> None:
    response.headers["X-CrocLens-Request-Id"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
