# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    API_BASE_URL=https://api.openai.com/v1 \
    MODEL_NAME=gpt-4.1-mini \
    USE_LLM=false \
    LOG_LEVEL=INFO

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 7860 available to the world outside this container
EXPOSE 7860

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/', timeout=5)" || exit 1

# Run uvicorn server with graceful shutdown
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]
