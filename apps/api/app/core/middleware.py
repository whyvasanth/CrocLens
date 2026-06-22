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
        request.state.request_id = request_id
        client_key = request.client.host if request.client else "unknown"
        started_at = time.perf_counter()

        if self._is_rate_limited(client_key):
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please wait briefly before trying again.",
                    "request_id": request_id,
                },
            )
            self._log_request(request, response, started_at, "rate_limited")
        else:
            try:
                response = await call_next(request)
                self._log_request(request, response, started_at)
            except Exception as exc:
                logger.exception(
                    "unhandled_api_error",
                    extra={
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "error_category": exc.__class__.__name__,
                        "user_id": getattr(request.state, "user_id", None),
                    },
                )
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "detail": "CrocLens hit an unexpected error. No internal details were exposed.",
                        "request_id": request_id,
                    },
                )
                self._log_request(request, response, started_at, exc.__class__.__name__)

        _add_security_headers(response, request_id)
        return response

    def _log_request(
        self,
        request: Request,
        response: Response,
        started_at: float,
        error_category: str | None = None,
    ) -> None:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.info(
            "request_completed",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "user_id": getattr(request.state, "user_id", None),
                "error_category": error_category,
            },
        )

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
