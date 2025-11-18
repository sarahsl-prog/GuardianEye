#!/bin/bash
# Development startup script

echo "Starting GuardianEye in development mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Start services with docker-compose
echo "Starting services (PostgreSQL, Redis, Ollama)..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Setup database
echo "Setting up database..."
python scripts/setup_db.py

# Start FastAPI application
echo "Starting FastAPI application..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
