from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from app.models import SimulationRequest, SimulationResponse
from app.simulation.engine import run_simulation
from app.simulation.analyzer import analyze_simulation
from app.templates import get_templates

app = FastAPI(title="Distributed Systems Lab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/templates")
def list_templates():
    return get_templates()

@app.post("/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest):
    try:
        # 1. Run TICK based simulation
        history = run_simulation(req.graph, req.duration_ticks, req.failures_injected)
        
        # 2. Analyze results to build explanation
        explanation = analyze_simulation(history, req.graph)
        
        return SimulationResponse(
            history=history,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
