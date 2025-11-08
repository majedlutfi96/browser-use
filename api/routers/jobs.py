"""Job management API routes.

This module defines the REST API endpoints for creating,
retrieving, and managing browser automation jobs.
"""

from hashlib import sha256

from fastapi import APIRouter, BackgroundTasks, HTTPException, Path, status
from pydantic import BaseModel, Field

from models.job import Job
from services.job_service import run_job

router = APIRouter(
    prefix="",
    tags=["jobs"],
)


class JobCreate(BaseModel):
    """
    Request model for creating a new job.
    
    Attributes:
        task: Natural language description of the task to perform
        overwrite: If True, recreate job even if it exists (default: False)
        timeout: Maximum execution time in seconds (default: 300)
    """
    task: str = Field(
        ...,
        description="Natural language task description for the browser agent",
        examples=["Search for Python tutorials on YouTube", "Get the current price of Bitcoin from CoinMarketCap"]
    )
    overwrite: bool = Field(
        False,
        description="If True, overwrite existing job with same task; if False, return existing job"
    )
    timeout: int = Field(
        60 * 5,
        description="Maximum execution time in seconds",
        ge=1,
        le=3600
    )


@router.post(
    "/jobs",
    response_model=Job,
    status_code=status.HTTP_200_OK,
    summary="Create a new job",
    description="""
    Create a new browser automation job or return an existing one.
    
    The job is identified by a SHA256 hash of the task description.
    If a job with the same task already exists and `overwrite` is False,
    the existing job is returned. Otherwise, a new job is created and
    executed asynchronously in the background.
    
    **Job Lifecycle:**
    1. Job created with status 'pending'
    2. Background task starts execution
    3. Status changes to 'running'
    4. Upon completion, status becomes 'completed' with results
    5. If timeout exceeded, status becomes 'timedOut'
    """,
    responses={
        200: {
            "description": "Job created successfully or existing job returned",
            "content": {
                "application/json": {
                    "example": {
                        "id": "a1b2c3d4e5f6...",
                        "task": "Get the current price of Bitcoin",
                        "result": None,
                        "status": "pending",
                        "createdAt": "2024-01-01T12:00:00.000Z",
                        "updatedAt": None,
                        "timeout": 300
                    }
                }
            }
        },
        401: {"description": "Invalid or missing API key"}
    }
)
def create_job(job_data: JobCreate, background_tasks: BackgroundTasks) -> Job:
    """
    Create a new browser automation job.
    
    Args:
        job_data: Job creation parameters
        background_tasks: FastAPI background tasks manager
        
    Returns:
        Job: The created or existing job instance
        
    Note:
        Jobs with identical tasks share the same ID (SHA256 hash).
        Set overwrite=True to force recreation of an existing job.
    """
    job_id = sha256(job_data.task.encode()).hexdigest()

    job = Job.get_job(job_id)
    if job and not job_data.overwrite:
        return job

    job = Job(task=job_data.task)
    background_tasks.add_task(run_job, job)

    return job


@router.get(
    "/jobs/{job_id}",
    response_model=Job,
    summary="Get job by ID",
    description="""
    Retrieve a specific job by its unique identifier.
    
    The job ID is a SHA256 hash of the task description.
    Returns the current state of the job including status and results.
    """,
    responses={
        200: {
            "description": "Job found and returned",
            "content": {
                "application/json": {
                    "example": {
                        "id": "a1b2c3d4e5f6...",
                        "task": "Get the current price of Bitcoin",
                        "result": "The current price of Bitcoin is $45,123.45",
                        "status": "completed",
                        "createdAt": "2024-01-01T12:00:00.000Z",
                        "updatedAt": "2024-01-01T12:01:30.000Z",
                        "timeout": 300
                    }
                }
            }
        },
        404: {"description": "Job not found"},
        401: {"description": "Invalid or missing API key"}
    }
)
def get_job(job_id: str = Path(..., description="Unique job identifier (SHA256 hash)")) -> Job:
    """
    Retrieve a job by its ID.
    
    Args:
        job_id: The unique identifier of the job
        
    Returns:
        Job: The job instance with current status and results
        
    Raises:
        HTTPException: 404 if job not found
    """
    job = Job.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get(
    "/jobs",
    response_model=list[Job],
    summary="List all jobs",
    description="""
    Retrieve all jobs from the system.
    
    Returns a list of all jobs regardless of their status.
    Jobs are not sorted in any particular order.
    """,
    responses={
        200: {
            "description": "List of all jobs",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "a1b2c3d4e5f6...",
                            "task": "Get Bitcoin price",
                            "result": "$45,123.45",
                            "status": "completed",
                            "createdAt": "2024-01-01T12:00:00.000Z",
                            "updatedAt": "2024-01-01T12:01:30.000Z",
                            "timeout": 300
                        },
                        {
                            "id": "b2c3d4e5f6a7...",
                            "task": "Search Python tutorials",
                            "result": None,
                            "status": "running",
                            "createdAt": "2024-01-01T12:05:00.000Z",
                            "updatedAt": "2024-01-01T12:05:10.000Z",
                            "timeout": 300
                        }
                    ]
                }
            }
        },
        401: {"description": "Invalid or missing API key"}
    }
)
def get_jobs() -> list[Job]:
    """
    Retrieve all jobs.
    
    Returns:
        list[Job]: List of all job instances in the system
    """
    return Job.get_jobs()
