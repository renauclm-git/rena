#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$PROJECT_ROOT/scripts/install.sh"

echo "Starting backend and frontend..."

echo "Backend running on http://localhost:5000"
source "$PROJECT_ROOT/backend/.venv/bin/activate"
python "$PROJECT_ROOT/backend/app.py" &
BACKEND_PID=$!

echo "Frontend running on http://localhost:5173"
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

trap 'kill "$BACKEND_PID" "$FRONTEND_PID"' EXIT

wait "$BACKEND_PID" "$FRONTEND_PID"
