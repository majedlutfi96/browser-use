import os

# Job storage configuration
JOBS_DIRECTORY = os.getenv("JOBS_DIRECTORY", "jobs_directory")

# Ensure jobs directory exists
if not os.path.exists(JOBS_DIRECTORY):
    os.makedirs(JOBS_DIRECTORY)
