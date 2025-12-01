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

# Create log files
touch backend.log frontend.log

# Check Node Version
NODE_VER=$(node -v)
echo "ℹ️  Node Version: $NODE_VER"

# Start Backend
echo "📂 Starting Backend (API)..."
cd tbnt-api
# Use full path if possible, or rely on PATH. Logging to file for debugging.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
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
tail -f ../backend.log ../frontend.log
