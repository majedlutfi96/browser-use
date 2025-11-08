"""Authentication middleware.

This module provides API key-based authentication middleware
for securing API endpoints.
"""

import os
from secrets import compare_digest

from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class CheckApiKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key authentication.
    
    Validates the X-API-Key header against the configured API_KEY
    environment variable. Uses constant-time comparison to prevent
    timing attacks.
    
    Exempted Endpoints:
        - /health: Health check endpoint (no authentication required)
        - /docs: Swagger UI documentation (no authentication required)
        - /redoc: ReDoc documentation (no authentication required)
        - /openapi.json: OpenAPI schema (no authentication required)
        
    Environment Variables:
        API_KEY: The valid API key for authentication
        
    Headers:
        X-API-Key: Client must provide this header with valid API key
        
    Responses:
        401 Unauthorized: If API key is missing or invalid
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request and validate API key.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or endpoint handler
            
        Returns:
            Response: Either the next handler's response or a 401 error
            
        Note:
            The /health endpoint bypasses authentication.
            Uses constant-time comparison to prevent timing attacks.
        """
        # Exempt documentation and health endpoints from authentication
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        api_key = os.getenv("API_KEY", "")
        request_api_key = request.headers.get("X-API-Key", "")

        if not compare_digest(request_api_key, api_key):
            return JSONResponse(status_code=401, content={"detail": "Invalid API key"})

        response = await call_next(request)
        return response
