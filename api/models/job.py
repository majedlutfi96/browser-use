import json
import os
from datetime import datetime, timezone
from hashlib import sha256

from pydantic import BaseModel

from config import JOBS_DIRECTORY


class Job(BaseModel):
    id: str | None = None
    task: str
    result: str | None = None
    status: str = "pending"
    createdAt: str = datetime.now(tz=timezone.utc).isoformat()
    updatedAt: str | None = None
    timeout: int = 60 * 5

    @staticmethod
    def get_job(job_id: str) -> "Job | None":
        if os.path.exists(os.path.join(JOBS_DIRECTORY, job_id + ".json")):
            with open(os.path.join(JOBS_DIRECTORY, job_id + ".json"), "r") as f:
                job = Job(**json.load(f))
                if job.status == "running" and job.timed_out:
                    job.update(status="timedOut")
                return job
        return None

    def __init__(
        self,
        task: str,
        id: str | None = None,
        result: str | None = None,
        status: str = "pending",
        createdAt: str = datetime.now(tz=timezone.utc).isoformat(),
        updatedAt: str | None = None,
        timeout: int = 60 * 5,
    ) -> None:
        super().__init__(
            task=task,
            id=sha256(task.encode()).hexdigest(),
            result=result,
            status=status,
            createdAt=createdAt,
            updatedAt=updatedAt,
            timeout=timeout,
        )
        self.save()

    def save(self) -> None:
        with open(os.path.join(JOBS_DIRECTORY, self.id + ".json"), "w") as f:
            json.dump(self.model_dump(), f)

    def update(self, **kwargs) -> None:
        self.updatedAt = datetime.now(tz=timezone.utc).isoformat()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def delete(self) -> None:
        os.remove(os.path.join(JOBS_DIRECTORY, self.id + ".json"))

    @staticmethod
    def get_jobs() -> list["Job"]:
        return [
            Job.get_job(job_id.rstrip(".json")) for job_id in os.listdir(JOBS_DIRECTORY)
        ]

    @property
    def timed_out(self) -> bool:
        return (
            datetime.now(tz=timezone.utc) - datetime.fromisoformat(self.createdAt)
        ).total_seconds() > self.timeout
