# Use the official Python image as the base image
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /usr/src/app

# Copy the rest of the code into the container
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir .

# Set the command to run your application
CMD ["python", "./main.py"]
