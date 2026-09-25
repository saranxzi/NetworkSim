import math
from dataclasses import dataclass
from networksim.finops.catalog import get_price

@dataclass(slots=True)
class CostBreakdown:
    hourly: float
    monthly: float
    compute: float
    egress: float
    storage: float

class CostCalculator:
    __slots__ = ()

    def estimate_node_cost(
        self,
        node_type: str,
        provider: str,
        region: str,
        avg_throughput_rps: float,
        avg_egress_gb_per_hour: float = 0.0
    ) -> CostBreakdown:
        entry = get_price(provider, node_type, region) or get_price(provider, "api_server", region)
        if not entry:
            return CostBreakdown(0.0, 0.0, 0.0, 0.0, 0.0)

        capacity = entry.capacity_rps or 1000
        instances_needed = max(1, math.ceil(avg_throughput_rps / capacity)) if capacity > 0 else 1

        compute_hourly = instances_needed * entry.hourly_cost_usd
        egress_hourly = avg_egress_gb_per_hour * entry.egress_cost_per_gb
        storage_hourly = 0.0

        hourly = compute_hourly + egress_hourly + storage_hourly
        monthly = hourly * 730  # Approx 730 hours/month

        return CostBreakdown(
            hourly=hourly,
            monthly=monthly,
            compute=compute_hourly * 730,
            egress=egress_hourly * 730,
            storage=storage_hourly * 730
        )

    def estimate_graph_cost(self, nodes: dict[str, dict], provider: str, region: str) -> dict[str, CostBreakdown]:
        return {
            nid: self.estimate_node_cost(
                nodedata.get("type", "api_server"),
                provider,
                region,
                nodedata.get("throughput", 0.0),
                nodedata.get("egress_gb", 0.0)
            )
            for nid, nodedata in nodes.items()
        }

    def total_monthly_cost(self, breakdowns: dict[str, CostBreakdown]) -> float:
        return sum(b.monthly for b in breakdowns.values())
