from browser_use import Agent

from models.job import Job
from services.agent_service import configure_agent


async def run_job(job: Job) -> None:
    """
    Execute a job by running the browser agent.
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
