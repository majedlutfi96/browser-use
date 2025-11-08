"""Agent configuration service.

This module provides functions to configure and initialize
the browser automation agent and its dependencies.
"""

import os

from browser_use import Browser, ChatGoogle


def configure_agent() -> tuple[Browser, ChatGoogle]:
    """
    Configure and initialize the browser and LLM for the agent.
    
    Creates a headless browser instance and configures the Google Gemini
    language model for agent operations.
    
    Returns:
        tuple[Browser, ChatGoogle]: A tuple containing:
            - Browser: Configured headless browser instance
            - ChatGoogle: Configured Google Gemini LLM instance
            
    Environment Variables:
        GOOGLE_API_KEY: Required API key for Google Gemini access
        
    Example:
        >>> browser, llm = configure_agent()
        >>> # Use browser and llm with Agent
    """
    browser = Browser(
        headless=True,
    )
    llm = ChatGoogle(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
    )
    return (browser, llm)
