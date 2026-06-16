FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for certain lockfiles/packages if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files and database configurations
COPY backend/ /app/backend/
COPY datasets/ /app/datasets/
COPY reports/ /app/reports/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/alembic.ini

# Set Python path
ENV PYTHONPATH=/app

EXPOSE 8000

# Run migrations, seed default admin, and start FastAPI
CMD ["sh", "-c", "alembic upgrade head && python backend/database/seed_admin.py && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
