#!/bin/bash

# Function to kill processes on exit
cleanup() {
    echo "🛑 Stopping all services..."
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
    exit
}

# Set up trap to catch SIGINT (Ctrl+C)
trap cleanup SIGINT

echo "🚀 Starting TBNT Project..."

# Kill any existing processes on ports 8000 and 5173
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
echo "✅ Ports 8000 and 5173 are clear."

# Create log files
touch backend.log frontend.log

# Check Node Version
NODE_VER=$(node -v)
echo "ℹ️  Node Version: $NODE_VER"

# Start Backend
echo "📂 Starting Backend (API)..."
cd tbnt-api

# Check if conda is installed and try to run with tbnt_env
if command -v conda >/dev/null 2>&1; then
    echo "✅ Conda detected. Using environment 'tbnt_env'..."
    conda run -n tbnt_env --no-capture-output uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
else
    echo "⚠️  Conda not found. Trying to run uvicorn directly..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
fi

BACKEND_PID=$!
echo "✅ Backend started with PID $BACKEND_PID (Logs: backend.log)"

# Go back to root
cd ..

# Start Frontend
echo "📂 Starting Frontend (Web)..."
cd tbnt-web
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started with PID $FRONTEND_PID (Logs: frontend.log)"

echo "📋 Tailing logs (Press Ctrl+C to stop)..."
tail -f backend.log frontend.log
