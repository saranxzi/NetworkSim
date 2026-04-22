"""Physics evaluation for simulation nodes."""
from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class NodeState:
    id: str
    label: str
    node_type: str
    capacity: float
    base_latency: float
    base_rps: float
    burst_factor: float
    
    status: str = "healthy"
    current_rps: float = 0.0
    queue_depth: int = 0
    drop_rate: float = 0.0
    current_latency: float = 0.0
    
    cb_state: str = "closed"
    cb_failure_count: int = 0
    cb_cooldown_remaining: int = 0
    
    tb_tokens: float = 0.0
    tb_capacity: float = 0.0
    tb_refill_rate: float = 0.0
    
    @classmethod
    def from_pydantic(cls, nid: str, model) -> "NodeState":
        # Resolve effective capacity: databases use write_capacity, others use capacity
        raw_capacity = getattr(model, "capacity", None)
        write_cap = getattr(model, "write_capacity", None)
        read_cap = getattr(model, "read_capacity", None)
        
        if model.type == "database":
            effective_capacity = write_cap or read_cap or raw_capacity or 500.0
        else:
            effective_capacity = raw_capacity or 1000.0
        
        return cls(
            id=nid,
            label=model.label,
            node_type=model.type,
            capacity=effective_capacity,
            base_latency=getattr(model, "base_latency", None) or 10.0,
            base_rps=getattr(model, "base_rps", None) or 0.0,
            burst_factor=getattr(model, "burst_factor", None) or 1.0,
            status=model.status,
            current_rps=model.throughput,
            queue_depth=model.queue_depth,
            drop_rate=model.drop_rate,
            current_latency=model.latency,
        )

# Maximum queue buffer per node
MAX_QUEUE_DEPTH = 10_000

def evaluate_node_physics(node: NodeState, incoming_rps: float, events: List[str], node_id: str) -> None:
    """Evaluate node physics using M/M/c/K queuing model. Mutates node in-place."""
    if node.node_type == "client":
        node.current_rps = incoming_rps
        node.status = "healthy"
        return

    if node.status == "failed" or node.capacity <= 0:
        node.current_rps = 0.0
        node.drop_rate = incoming_rps
        node.current_latency = 0.0
        return

    # Total demand = new arrivals + queued backlog
    total_demand = incoming_rps + node.queue_depth

    if total_demand <= node.capacity:
        # HEALTHY: Can serve everything (new traffic + drain entire queue)
        node.current_rps = total_demand  # Forward all including drained queue
        node.queue_depth = 0
        node.drop_rate = 0.0
        node.current_latency = node.base_latency
        if node.status == "critical":
            events.append(f"Recovery at {node_id}")
        node.status = "healthy" if total_demand / node.capacity < 0.8 else "warning"
    elif incoming_rps <= node.capacity:
        # WARNING: Can serve all new traffic, partially drain queue
        spare = node.capacity - incoming_rps
        drained = min(spare, node.queue_depth)
        node.current_rps = incoming_rps + drained  # Forward new + drained
        node.queue_depth = max(0, node.queue_depth - int(drained))
        node.drop_rate = 0.0
        rho = total_demand / node.capacity if node.capacity > 0 else 1.0
        node.current_latency = node.base_latency / (1.0 - min(rho, 0.99) + 0.01)
        node.status = "warning"
    else:
        # CRITICAL: New arrivals exceed capacity
        # Process at capacity
        node.current_rps = node.capacity
        excess = incoming_rps - node.capacity
        # Queue what fits in the buffer
        space_in_queue = max(0, MAX_QUEUE_DEPTH - node.queue_depth)
        queued = min(excess, space_in_queue)
        dropped = excess - queued
        node.queue_depth += int(queued)
        node.drop_rate = dropped
        # Latency from Little's Law: L = lambda * W => W = L / lambda
        node.current_latency = node.base_latency + (node.queue_depth / node.capacity) * 1000
        if node.status != "critical":
            events.append(f"Capacity exceeded at {node_id}")
        node.status = "critical"
