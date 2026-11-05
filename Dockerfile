# UZEX Spot AI Agent Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Build SQLite database and summary tables (~50 seconds)
RUN python db_builder.py

# Expose FastAPI web service port
EXPOSE 8000

# Default: start bot
CMD ["python", "bot.py"]
