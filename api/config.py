"""
Configuration module for the Browser Use API.

This module manages application-wide configuration settings,
including environment variables and directory setup.
"""

import os

# Job storage configuration
JOBS_DIRECTORY = os.getenv("JOBS_DIRECTORY", "jobs_directory")
"""str: Directory path where job data is persisted as JSON files.
Can be overridden via the JOBS_DIRECTORY environment variable.
"""

# Ensure jobs directory exists
if not os.path.exists(JOBS_DIRECTORY):
    os.makedirs(JOBS_DIRECTORY)
