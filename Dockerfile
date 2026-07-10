FROM python:3.11-slim

WORKDIR /workspace

# Install essential system compilation packages required for PostgreSQL compilation extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app folder and frontend directory assets
COPY ./app ./app
COPY ./frontend ./frontend

EXPOSE 8000

# Boot FastAPI and serve the static files on port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
