#!/bin/bash

# Voice Dialogue Studio - Unified Start Script
echo "🎙️ Starting Voice Dialogue Studio..."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down Voice Dialogue Studio..."
    
    # Kill backend process
    if [ ! -z "$BACKEND_PID" ]; then
        echo "📡 Stopping backend..."
        kill $BACKEND_PID 2>/dev/null
        wait $BACKEND_PID 2>/dev/null
    fi
    
    # Kill frontend process  
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "🌐 Stopping frontend..."
        kill $FRONTEND_PID 2>/dev/null
        wait $FRONTEND_PID 2>/dev/null
    fi
    
    # Clean up any remaining processes
    pkill -f "python3 backend_api.py" 2>/dev/null
    pkill -f "npm run dev" 2>/dev/null
    
    echo "✅ All services stopped"
    exit 0
}

# Set up trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Check if Python backend dependencies are installed
echo "📦 Checking Python dependencies..."
if ! python3 -c "import fastapi, uvicorn, pyneuphonic" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements-api.txt 2>/dev/null || pip3 install fastapi uvicorn python-multipart pydantic
    pip3 install pyneuphonic 2>/dev/null || echo "⚠️ pyneuphonic may need manual installation"
fi

# Check if Node.js frontend dependencies are installed
echo "📦 Checking Node.js dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install --legacy-peer-deps
fi

# Start the FastAPI backend in the background
echo "🚀 Starting FastAPI backend (port 8000)..."
python3 backend_api.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "❌ Backend failed to start"
        exit 1
    fi
    sleep 1
done

# Start the Next.js frontend
echo "🌐 Starting Next.js frontend (port 3000)..."
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
for i in {1..20}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "❌ Frontend failed to start"
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎉 Voice Dialogue Studio is now running!"
echo ""
echo "📡 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🌐 Frontend: http://localhost:3000"
echo ""
echo "📊 Backend Health: $(curl -s http://localhost:8000/health | jq -r '.message' 2>/dev/null || echo 'Checking...')"
echo ""
echo "💡 Press Ctrl+C to stop both services"
echo ""

# Monitor processes and wait
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend process died, restarting..."
        python3 backend_api.py &
        BACKEND_PID=$!
        sleep 3
    fi
    
    # Check if frontend is still running  
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend process died, restarting..."
        npm run dev &
        FRONTEND_PID=$!
        sleep 3
    fi
    
    sleep 5
done 