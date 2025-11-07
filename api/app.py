from fastapi import FastAPI
from routers import router as jobs_router

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI()
    app.include_router(jobs_router)

    @app.get("/health")
    async def health_check():
        """
        Health check endpoint.
        """
        return {"status": "ok"}

    return app
    