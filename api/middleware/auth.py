import os
from secrets import compare_digest

from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class CheckApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path == "/health":
            return await call_next(request)
        
        api_key = os.getenv("API_KEY", "")
        request_api_key = request.headers.get("X-API-Key", "")

        if not compare_digest(request_api_key, api_key):
            return JSONResponse(status_code=401, content={"detail": "Invalid API key"})

        response = await call_next(request)
        return response
