#!/bin/bash
# Run from anywhere — always uses the project root as the working directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting Hermes Dashboard API..."
echo "  Backend : http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
echo ""

source venv/bin/activate 2>/dev/null || true
uvicorn dashboard.app:app --app-dir . --reload --port 8000
