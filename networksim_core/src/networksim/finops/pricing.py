from dataclasses import dataclass
from typing import Dict, Any
from networksim.finops.catalog import get_price

@dataclass(slots=True)
class CostBreakdown:
    hourly: float
    monthly: float
    compute: float
    egress: float
    storage: float

class CostCalculator:
    def estimate_node_cost(self, node_type: str, provider: str, region: str, avg_throughput_rps: float, avg_egress_gb_per_hour: float) -> CostBreakdown:
        entry = get_price(provider, node_type, region)
        if not entry:
            entry = get_price(provider, "api_server", region)
            
        if not entry:
            return CostBreakdown(0.0, 0.0, 0.0, 0.0, 0.0)
            
        capacity = entry.capacity_rps
        instances_needed = max(1, int(avg_throughput_rps / capacity) + (1 if avg_throughput_rps % capacity > 0 else 0))
        
        compute_hourly = instances_needed * entry.hourly_cost_usd
        egress_hourly = avg_egress_gb_per_hour * entry.egress_cost_per_gb
        storage_hourly = 0.0  # Simplification
        
        hourly = compute_hourly + egress_hourly + storage_hourly
        monthly = hourly * 730  # Approx 730 hours/month
        
        return CostBreakdown(
            hourly=hourly,
            monthly=monthly,
            compute=compute_hourly * 730,
            egress=egress_hourly * 730,
            storage=storage_hourly * 730
        )

    def estimate_graph_cost(self, nodes: Dict[str, dict], provider: str, region: str) -> Dict[str, CostBreakdown]:
        breakdowns = {}
        for nid, nodedata in nodes.items():
            # Get type, fallback to api_server
            ntype = nodedata.get("type", "api_server")
            throughput = nodedata.get("throughput", 0.0)
            egress = nodedata.get("egress_gb", 0.0)
            
            breakdowns[nid] = self.estimate_node_cost(ntype, provider, region, throughput, egress)
        return breakdowns
        
    def total_monthly_cost(self, breakdowns: Dict[str, CostBreakdown]) -> float:
        return sum(b.monthly for b in breakdowns.values())
