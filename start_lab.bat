@echo off
echo Starting Interactive System Design Lab...

echo Starting Backend Simulation Engine (FastAPI on Port 8000)...
start cmd /k "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Frontend Canvas (Next.js on Port 3000)...
start cmd /k "npm run dev"

echo All services starting! The Next.js frontend will be available at http://localhost:3000
