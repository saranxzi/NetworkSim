"""NetworkSim API — FastAPI application with lifecycle management."""

import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.models import SimulationRequest, SimulationResponse, ExplanationOutput, SimulationTickResult, CanvasGraph
from networksim import run_simulation
from app.simulation.analyzer import analyze_simulation
from app.templates import get_templates
from app.deps import get_current_user, get_optional_user, CurrentUser

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    # Startup
    from app.logging_config import setup_logging
    from app.db import init_db
    from app.cache import init_redis
    
    setup_logging()
    await init_db()
    await init_redis()
    logger.info("NetworkSim API started")
    
    yield
    
    # Shutdown
    from app.db import close_db
    from app.cache import close_redis
    
    await close_redis()
    await close_db()
    logger.info("NetworkSim API stopped")


app = FastAPI(title="Distributed Systems Lab API", lifespan=lifespan)

# Restrict CORS origins to known frontends
import os
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# --- Mount API routers ---
from app.routes.blueprints import router as blueprints_router
from app.routes.runs import router as runs_router
from app.routes.finops import router as finops_router

app.include_router(blueprints_router, prefix="/api/blueprints", tags=["blueprints"])
app.include_router(runs_router, prefix="/api/runs", tags=["runs"])
app.include_router(finops_router, prefix="/api/finops", tags=["finops"])


# --- Existing routes (backward compatible) ---

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/templates")
def list_templates():
    return get_templates()

@app.post("/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest):
    try:
        history = run_simulation(req.graph, req.duration_ticks, req.failures_injected, seed=getattr(req, "seed", 0))
        explanation = analyze_simulation(history, req.graph)
        return SimulationResponse(
            history=history,
            explanation=explanation
        )
    except Exception as e:
        logger.exception("Simulation failed")
        raise HTTPException(status_code=500, detail="Simulation engine encountered an internal error.")


class AnalyzeRequest(BaseModel):
    history: List[SimulationTickResult]
    graph: CanvasGraph

@app.post("/analyze", response_model=ExplanationOutput)
def analyze_endpoint(req: AnalyzeRequest):
    try:
        return analyze_simulation(req.history, req.graph)
    except Exception as e:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=500, detail="Analysis engine encountered an internal error.")

@app.websocket("/ws/simulate")
async def websocket_simulate(websocket: WebSocket):
    """Delegates to the dedicated WebSocket handler with backpressure support."""
    from app.ws_handler import handle_simulation_ws
    await handle_simulation_ws(websocket)
