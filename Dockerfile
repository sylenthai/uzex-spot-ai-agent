# UZEX Spot AI Agent Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Build SQLite database and summary tables
RUN python db_builder.py

# Expose FastAPI web service port
EXPOSE 8000

# Default: start both bot and web service or bot
CMD ["python", "bot.py"]
