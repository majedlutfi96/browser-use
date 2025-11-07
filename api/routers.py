from fastapi import APIRouter

router = APIRouter()

@router.post("/jobs")
def create_job():
    return {"message": "Job created"}

@router.get("/jobs/{job_id}")
def get_job(job_id: int):
    return {"job_id": job_id}
