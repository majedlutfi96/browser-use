from fastapi import FastAPI

from middleware.auth import CheckApiKeyMiddleware
from routers.jobs import router as jobs_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI()
    app.add_middleware(CheckApiKeyMiddleware)
    app.include_router(jobs_router)

    @app.get("/health")
    async def health_check():
        """
        Health check endpoint.
        """
        return {"status": "ok"}

    return app
