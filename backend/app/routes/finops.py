from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from networksim.finops import CostCalculator, list_providers, list_regions
from networksim.finops.catalog import CATALOG

router = APIRouter()

class EstimateRequest(BaseModel):
    nodes: Dict[str, Any]
    provider: str
    region: str

@router.post("/estimate")
async def estimate_cost(req: EstimateRequest):
    calculator = CostCalculator()
    breakdowns = calculator.estimate_graph_cost(req.nodes, req.provider, req.region)
    total = calculator.total_monthly_cost(breakdowns)
    
    return {
        "total_monthly": total,
        "nodes": {k: {
            "hourly": v.hourly,
            "monthly": v.monthly,
            "compute": v.compute,
            "egress": v.egress,
            "storage": v.storage
        } for k, v in breakdowns.items()}
    }

@router.get("/catalog")
async def get_catalog():
    return [
        {
            "provider": v.provider,
            "resource_type": v.resource_type,
            "region": v.region,
            "hourly_cost_usd": v.hourly_cost_usd,
            "capacity_rps": v.capacity_rps,
            "egress_cost_per_gb": v.egress_cost_per_gb
        } for v in CATALOG.values()
    ]

@router.get("/providers")
async def get_providers():
    return list_providers()
