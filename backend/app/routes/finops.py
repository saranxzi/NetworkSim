from dataclasses import asdict
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel
from networksim.finops import CostCalculator, list_providers
from networksim.finops.catalog import CATALOG

router = APIRouter()

class EstimateRequest(BaseModel):
    nodes: dict[str, Any]
    provider: str
    region: str

@router.post("/estimate")
def estimate_cost(req: EstimateRequest):
    calculator = CostCalculator()
    breakdowns = calculator.estimate_graph_cost(req.nodes, req.provider, req.region)
    total = calculator.total_monthly_cost(breakdowns)
    
    return {
        "total_monthly": total,
        "nodes": {k: asdict(v) for k, v in breakdowns.items()}
    }

@router.get("/catalog")
def get_catalog():
    return [asdict(v) for v in CATALOG.values()]

@router.get("/providers")
def get_providers():
    return list_providers()
