from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.app.config.config import settings


class DomainLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if getattr(settings, "ENVIRONMENT", None) in ("DEV", "local"):
            return await call_next(request)
        host = request.headers.get("host", "")
        if host == "www.code-ground.com" or host == "code-ground.com":
            return await call_next(request)
        return JSONResponse(
            status_code=403,
            content={"detail": "Forbidden: Only official domain access is allowed."},
        )