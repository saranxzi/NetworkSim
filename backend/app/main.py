from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import json

from app.models import SimulationRequest, SimulationResponse, ExplanationOutput
from app.simulation.engine import run_simulation, run_simulation_stream
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

from typing import List
from app.models import SimulationTickResult, CanvasGraph
from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    history: List[SimulationTickResult]
    graph: CanvasGraph

@app.post("/analyze", response_model=ExplanationOutput)
def analyze_endpoint(req: AnalyzeRequest):
    try:
        return analyze_simulation(req.history, req.graph)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/simulate")
async def websocket_simulate(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        payload = json.loads(data)
        
        # Manually construct Pydantic models from dict for the stream
        from app.models import CanvasGraph
        graph_obj = CanvasGraph(**payload.get("graph", {}))
        duration = payload.get("duration_ticks", 60)
        failures = payload.get("failures_injected", [])
        chaos_mode = payload.get("chaos_mode", False)
        
        # Async stream
        async for tick_result in run_simulation_stream(graph_obj, duration, failures, chaos_mode):
            await websocket.send_text(tick_result.model_dump_json())
            
        await websocket.close()
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WS Error: {e}")
        try:
            await websocket.close(code=1011)
        except:
            pass
