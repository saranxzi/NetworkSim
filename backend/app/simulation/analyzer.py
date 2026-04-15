from app.models import SimulationTickResult, CanvasGraph, ExplanationOutput
from typing import List

def analyze_simulation(history: List[SimulationTickResult], graph: CanvasGraph) -> ExplanationOutput:
    if not history:
        return ExplanationOutput(narrative="Simulation failed to produce history.")

    final_state = history[-1]
    
    critical_nodes = []
    failed_nodes = []
    
    for node_id, node_data in final_state.nodes.items():
        if node_data.status == "critical":
            critical_nodes.append(node_id)
        elif node_data.status == "failed":
            failed_nodes.append(node_id)
            
    recommendations = []
    narrative = ""
    primary_bottleneck = None
    cascade_path = []

    if failed_nodes:
        primary_bottleneck = failed_nodes[0]
        node = final_state.nodes.get(primary_bottleneck)
        capacity = getattr(node, "capacity", 1)
        if hasattr(node, "write_capacity") and getattr(node, "write_capacity") is not None:
            capacity = getattr(node, "write_capacity")
            
        if capacity == 0.0:
            narrative = f"CATASTROPHIC OUTAGE: {primary_bottleneck} experienced a hard crash. Processing capacity plummeted to 0, blackholing all downstream traffic."
            recommendations.append(f"Investigate incident logs for {primary_bottleneck} immediately.")
            recommendations.append("Implement automated failover mechanisms (e.g. multi-AZ standby).")
        else:
            narrative = f"System collapsed. Volume at {primary_bottleneck} exponentially overwhelmed capacity, causing a total traffic drop."
            recommendations.append(f"Implement massive redundancy and circuit breakers for {primary_bottleneck}.")
            if "database" in getattr(node, "type", ""):
                recommendations.append("Deploy a Read Replica clustered fleet to offload DB traffic.")
            
    elif critical_nodes:
        primary_bottleneck = critical_nodes[0]
        node = final_state.nodes[primary_bottleneck]
        narrative = f"{primary_bottleneck} became a bottleneck. Incoming traffic exceeded capacity ({getattr(node, 'capacity', 'N/A')} req/s), causing a queue buildup of {getattr(node, 'queue_depth', 0)} requests."
        recommendations.append(f"Increase capacity or horizontally scale {primary_bottleneck}.")
        if "api_server" in getattr(node, "type", ""):
             recommendations.append("Add a Load Balancer to distribute API traffic.")
    else:
        narrative = "System ran perfectly under the simulated load. No bottlenecks detected."
        
    # very simple cascade path for demo
    if primary_bottleneck:
        cascade_path = [primary_bottleneck]

    return ExplanationOutput(
        primary_bottleneck=primary_bottleneck,
        cascade_path=cascade_path,
        narrative=narrative,
        recommendations=recommendations
    )
