"""Job model and persistence layer.

This module defines the Job data model and provides methods for
CRUD operations using file-based JSON storage.
"""

import json
import os
from datetime import datetime, timezone
from hashlib import sha256

from pydantic import BaseModel, Field

from config import JOBS_DIRECTORY


class Job(BaseModel):
    """
    Represents a browser automation job.
    
    A job encapsulates a task to be executed by the browser agent,
    along with its execution status, results, and metadata.
    
    Attributes:
        id: Unique identifier (SHA256 hash of the task)
        task: Description of the task to be performed
        result: Final result returned by the agent (None if not completed)
        status: Current status (pending, running, completed, timedOut)
        createdAt: ISO 8601 timestamp of job creation
        updatedAt: ISO 8601 timestamp of last update (None if never updated)
        timeout: Maximum execution time in seconds (default: 300)
    """
    id: str | None = Field(None, description="Unique job identifier (SHA256 hash)")
    task: str = Field(..., description="Task description for the browser agent")
    result: str | None = Field(None, description="Agent execution result")
    status: str = Field("pending", description="Job status: pending, running, completed, or timedOut")
    createdAt: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat(), description="Job creation timestamp (ISO 8601)")
    updatedAt: str | None = Field(None, description="Last update timestamp (ISO 8601)")
    timeout: int = Field(60 * 5, description="Maximum execution time in seconds")

    @staticmethod
    def get_job(job_id: str) -> "Job | None":
        """
        Retrieve a job by its ID from persistent storage.
        
        Args:
            job_id: The unique identifier of the job
            
        Returns:
            Job instance if found, None otherwise
            
        Note:
            If the job status is 'running' and it has timed out,
            the status will be automatically updated to 'timedOut'.
        """
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
        """
        Initialize a new Job instance and persist it to storage.
        
        Args:
            task: Description of the task to execute
            id: Optional job ID (auto-generated if not provided)
            result: Optional initial result
            status: Initial status (default: 'pending')
            createdAt: Creation timestamp (default: current UTC time)
            updatedAt: Last update timestamp (default: None)
            timeout: Execution timeout in seconds (default: 300)
            
        Note:
            The job is automatically saved to disk upon initialization.
            The ID is generated as a SHA256 hash of the task.
        """
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
        """
        Persist the job to disk as a JSON file.
        
        The job is saved to {JOBS_DIRECTORY}/{job_id}.json
        """
        with open(os.path.join(JOBS_DIRECTORY, self.id + ".json"), "w") as f:
            json.dump(self.model_dump(), f)

    def update(self, **kwargs) -> None:
        """
        Update job attributes and persist changes.
        
        Args:
            **kwargs: Arbitrary keyword arguments representing
                     attributes to update
                     
        Note:
            The updatedAt timestamp is automatically set to the current time.
            Changes are immediately persisted to disk.
        """
        self.updatedAt = datetime.now(tz=timezone.utc).isoformat()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def delete(self) -> None:
        """
        Delete the job from persistent storage.
        
        Raises:
            FileNotFoundError: If the job file doesn't exist
        """
        os.remove(os.path.join(JOBS_DIRECTORY, self.id + ".json"))

    @staticmethod
    def get_jobs() -> list["Job"]:
        """
        Retrieve all jobs from persistent storage.
        
        Returns:
            List of all Job instances found in the jobs directory
            
        Note:
            Jobs with 'running' status that have timed out will be
            automatically updated to 'timedOut' status.
        """
        return [
            Job.get_job(job_id.rstrip(".json")) for job_id in os.listdir(JOBS_DIRECTORY)
        ]

    @property
    def timed_out(self) -> bool:
        """
        Check if the job has exceeded its timeout duration.
        
        Returns:
            True if the job has been running longer than the timeout,
            False otherwise
            
        Note:
            Time is calculated from the createdAt timestamp.
        """
        return (
            datetime.now(tz=timezone.utc) - datetime.fromisoformat(self.createdAt)
        ).total_seconds() > self.timeout
