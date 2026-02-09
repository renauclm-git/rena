#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m venv "$PROJECT_ROOT/backend/.venv"
source "$PROJECT_ROOT/backend/.venv/bin/activate"

pip install --upgrade pip
pip install -r "$PROJECT_ROOT/backend/requirements.txt"

cd "$PROJECT_ROOT/frontend"
npm install

echo "Installation complete."
