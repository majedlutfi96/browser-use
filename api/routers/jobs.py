from hashlib import sha256

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from models.job import Job
from services.job_service import run_job

router = APIRouter()


class JobCreate(BaseModel):
    task: str
    overwrite: bool = (
        False  # If True, overwrite the job if it already exists otherwise it will return pervious result of the job exists
    )
    timeout: int = 60 * 5  # Timeout in seconds


@router.post("/jobs")
def create_job(job_data: JobCreate, background_tasks: BackgroundTasks) -> Job:
    job_id = sha256(job_data.task.encode()).hexdigest()

    job = Job.get_job(job_id)
    if job and not job_data.overwrite:
        return job

    job = Job(task=job_data.task)
    background_tasks.add_task(run_job, job)

    return job


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> Job:
    job = Job.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs")
def get_jobs() -> list[Job]:
    return Job.get_jobs()
