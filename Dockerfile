# Use an official Python image as a base
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Set Pipenv to create the virtual environment inside the project directory
ENV PIPENV_VENV_IN_PROJECT=1

# Copy the Pipfile and Pipfile.lock first (if available) to leverage Docker’s caching
COPY Pipfile Pipfile.lock* /app/

# Install dependencies using pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of the application files
COPY . /app

# Create a non-root user
RUN useradd --create-home appuser

# Give ownership of the /app directory to the new user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Set the command to run your script
CMD ["pipenv", "run", "python", "main.py"]
