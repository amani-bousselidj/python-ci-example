#!/bin/bash

# Portfolio Admin Dashboard API - Startup Script
# This script starts the FastAPI server

echo "Starting Portfolio Admin Dashboard API..."
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Starting server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Press CTRL+C to stop the server"
echo ""

# Start the server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
