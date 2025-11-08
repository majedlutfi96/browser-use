import os

from browser_use import Browser, ChatGoogle


def configure_agent() -> tuple[Browser, ChatGoogle]:
    """
    Configure the browser and LLM for the agent.
    """
    browser = Browser(
        headless=True,
    )
    llm = ChatGoogle(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
    )
    return (browser, llm)
