README

FastAPI Project

This repository contains a FastAPI application configured to run in a Dockerized environment, with database connections managed via environment variables. Below you will find instructions for setting up and running the application and tests.

Prerequisites
The application requires a .env file in the root directory for configuration. This file contains sensitive information for application and database settings.

Create a .env file
in the root of the project, create a .env file with the following content:

# # env
# Application Configuration
APP_CONFIG_FILE=app/config.yaml

APP_API_PORT=8000

AUTH_SECRET_KEY=<your_auth_secret_key_here>

# Database Configuration
POSTGRES_USER=postgres

POSTGRES_PASSWORD=<your_postgres_password_here>

POSTGRES_HOST=db

POSTGRES_PORT=5432

POSTGRES_DB=starnavi

# External API Keys
GEMINI_API_KEY=<your_gemini_api_key_here>

Note: Replace <your_auth_secret_key_here>, <your_postgres_password_here>, and <your_gemini_api_key_here> with your actual secret values. Keep this file secure and do not share it publicly, as it contains sensitive credentials.

Running the Application
To start the application, run the following command in the root directory:

bash
docker-compose -f docker-compose.yml up --build --abort-on-container-exit
This command will build the Docker image (if not already built), start the services defined in docker-compose.yml, and terminate all services if any container exits unexpectedly.

Running Tests
To run the automated tests, use the following command in the root directory:

bash
docker-compose -f docker-compose-test.yml up --build --abort-on-container-exit
This command uses a separate Docker Compose configuration (docker-compose-test.yml) for testing purposes. The test containers will start, execute all tests, and then exit.

Additional Notes
The application is configured to run on APP_API_PORT (default: 8000).
All database configurations (user, password, host, port, and database name) are pulled from the .env file.
Ensure that the .env file exists and is properly configured before starting the application.