"""Job execution service.

This module handles the execution of browser automation jobs
using the configured agent and manages job lifecycle.
"""

from browser_use import Agent

from models.job import Job
from services.agent_service import configure_agent


async def run_job(job: Job) -> None:
    """
    Execute a browser automation job using the configured agent.
    
    This function orchestrates the complete job execution lifecycle:
    1. Configures a fresh browser and LLM instance
    2. Creates an agent with the job's task
    3. Updates job status to 'running'
    4. Executes the agent
    5. Updates job with results and 'completed' status
    
    Args:
        job: The Job instance to execute
        
    Raises:
        Exception: Any exception raised during agent execution
                  (should be caught by caller)
                  
    Note:
        The job status is updated to 'running' before execution begins.
        Upon successful completion, the job is updated with the result
        and status 'completed'. Failures should be handled by the caller.
        
    Example:
        >>> job = Job(task="Search for Python tutorials")
        >>> await run_job(job)
        >>> print(job.status)  # 'completed'
        >>> print(job.result)  # Agent's final result
    """
    browser, llm = configure_agent()
    agent = Agent(
        task=job.task,
        llm=llm,
        browser=browser,
        timeout=job.timeout,
    )
    job.update(status="running")
    history = await agent.run()
    job.update(result=history.final_result(), status="completed")
