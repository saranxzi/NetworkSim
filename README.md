# NetworkSim (formerly FlightSim)

NetworkSim is a high-fidelity, real-time web application designed to simulate the physics, traffic flow, and failure states of massive distributed network architectures. It provides a visual, interactive canvas where users can build, monitor, and deliberately test complex microservice environments under simulated duress.

## Features & Recent Updates

*   **Interactive Architecture Canvas:** A drag-and-drop React Flow interface for building custom network topologies.
*   **Real-Time Physics Engine:** A Python-based (NetworkX) high-speed simulator calculating latency, bandwidth bottlenecks, and edge costs at 60 ticks per second.
*   **System Latency Tracking:** End-to-end system latency monitoring via deep instrumentation of both frontend and backend for real-world performance verification.
*   **Chaos Daemon:** An automated sub-system that selectively degrades or destroys nodes to test system resilience and routing intelligence.
*   **Live Telemetry & Gamified Billing:** Recharts-powered analytics for real-time monitoring of theoretical resource consumption and a dynamic, editable AWS costs tracking matrix.
*   **NLP Auto-Fix Terminal:** A natural language processing terminal console to diagnose and automatically repair degraded network architecture.

## Getting Started

### Local Development

This project utilizes Next.js 16 (on Turbopack) for the frontend and a Python-based FastAPI simulator for the physics backend.

#### Frontend
```bash
npm run dev
# or
yarn dev
```
Open [http://localhost:3000](http://localhost:3000) with your browser to see the visual environment.

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Architecture
- **Frontend Layer:** Next.js, React Flow, Zustand, Recharts, Tailwind CSS.
- **Simulation Layer:** FastAPI, NetworkX (Python DiGraph), Async Generators for 60-tick WebSocket payloads, Redis.

## Deployment
Docker support is baked in, allowing both backend and frontend layers to spin up reliably. Check `docker-compose.yml` for network settings.
