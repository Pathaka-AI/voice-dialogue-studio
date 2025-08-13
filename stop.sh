#!/bin/bash

# Voice Dialogue Studio - Stop Script
echo "🛑 Stopping Voice Dialogue Studio..."

# Kill processes by name
echo "📡 Stopping backend processes..."
pkill -f "python3 backend_api.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

echo "🌐 Stopping frontend processes..."
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "next-server" 2>/dev/null || true

# Kill processes by port
echo "🧹 Cleaning up ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

sleep 2

echo "✅ All Voice Dialogue Studio services stopped" 