"""FastAPI application factory.

This module creates and configures the FastAPI application instance
with all necessary middleware, routers, and metadata.
"""

from fastapi import FastAPI
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from middleware.auth import CheckApiKeyMiddleware
from routers.jobs import router as jobs_router

# Define API key security scheme for Swagger UI
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Initializes the FastAPI app with:
    - API metadata (title, description, version)
    - Authentication middleware
    - Job management routes
    - Health check endpoint
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="Browser Use API",
        description="""
        ## Browser Automation API
        
        ### Authentication
        
        All endpoints (except `/health`) require an API key:
        
        ```
        X-API-Key: your-api-key-here
        ```
        
        ### Job Lifecycle
        
        1. **pending** - Job created, waiting to execute
        2. **running** - Agent is actively working on the task
        3. **completed** - Task finished successfully with results
        4. **timedOut** - Task exceeded the timeout limit
        
        ### Example Usage
        
        ```python
        import requests
        
        headers = {"X-API-Key": "your-api-key"}
        
        # Create a job
        response = requests.post(
            "http://localhost:7777/jobs",
            json={"task": "Get the current Bitcoin price from CoinMarketCap"},
            headers=headers
        )
        job = response.json()
        
        # Check job status
        response = requests.get(
            f"http://localhost:7777/jobs/{job['id']}",
            headers=headers
        )
        print(response.json())
        ```
        """,
        version="1.0.0",
        contact={
            "name": "Browser Use API",
            "url": "https://github.com/browser-use/browser-use",
        },
        license_info={
            "name": "MIT",
        },
        openapi_tags=[
            {
                "name": "jobs",
                "description": "Operations for managing browser automation jobs",
            },
            {
                "name": "health",
                "description": "Health check and monitoring endpoints",
            }
        ]
    )
    
    # Customize OpenAPI schema to add security
    from fastapi.openapi.utils import get_openapi
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # Add security scheme
        openapi_schema["components"]["securitySchemes"] = {
            "APIKeyHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "Enter your API key"
            }
        }
        
        # Apply security to all endpoints except health and docs
        for path, path_item in openapi_schema["paths"].items():
            if path not in ["/health", "/docs", "/openapi.json"]:
                for operation in path_item.values():
                    if isinstance(operation, dict) and "security" not in operation:
                        operation["security"] = [{"APIKeyHeader": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    app.add_middleware(CheckApiKeyMiddleware)
    app.include_router(jobs_router)

    @app.get(
        "/health",
        tags=["health"],
        summary="Health check",
        description="Check if the API is running and healthy. No authentication required.",
        responses={
            200: {
                "description": "API is healthy",
                "content": {
                    "application/json": {
                        "example": {"status": "ok"}
                    }
                }
            }
        }
    )
    async def health_check():
        """
        Health check endpoint for monitoring and load balancers.
        
        Returns:
            dict: Status indicator
            
        Note:
            This endpoint does not require authentication.
        """
        return JSONResponse(content={"status": "ok"})

    return app
