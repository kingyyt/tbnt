#!/bin/bash

echo "🚀 Starting TBNT Project..."

# Kill any existing processes on ports 8000 and 5173
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Start Backend
echo "📂 Starting Backend..."
cd tbnt-api
# Check if conda is installed and try to run with tbnt_env
if command -v conda >/dev/null 2>&1; then
    conda run -n tbnt-env --no-capture-output uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
else
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
fi
cd ..

# Start Frontend
echo "📂 Starting Frontend..."
cd tbnt-web
npm run dev
