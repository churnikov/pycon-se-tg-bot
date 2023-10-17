# Use the official Python image as the base image
FROM python:3.10-slim-buster

# Install Poetry
RUN apt-get update && apt-get install -y curl
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

# Set the working directory
WORKDIR /usr/src/app

# Copy the dependencies file to the working directory
COPY pyproject.toml poetry.lock .

# Install the dependencies
RUN poetry install --no-root --no-cache --no-interaction

# Copy the rest of the code into the container
COPY . .

# Install the dependencies
RUN poetry install --no-dev --no-cache --no-interaction

# Set the command to run your application
CMD ["python", "./main.py"]
