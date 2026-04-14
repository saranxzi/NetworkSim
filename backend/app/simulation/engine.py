import networkx as nx
from typing import Dict, List, Any
import copy
from app.models import CanvasGraph, SimulationTickResult, BaseNodeData

def build_nx_graph(canvas_graph: CanvasGraph) -> nx.DiGraph:
    G = nx.DiGraph()
    for node_id, node_data in canvas_graph.nodes.items():
        G.add_node(node_id, data=node_data)
    for edge in canvas_graph.edges:
        G.add_edge(edge.source, edge.target)
    return G

def apply_failures(nodes: Dict[str, BaseNodeData], tick: int, failures: List[Dict[str, Any]]) -> List[str]:
    events = []
    for f in failures:
        if f.get("start_tick", 0) <= tick and f.get("end_tick", 999999) >= tick:
            node_id = f.get("node_id")
            if node_id in nodes:
                if getattr(nodes[node_id], "status", "") != "failed":
                    events.append(f"Injected failure at {node_id}")
                nodes[node_id].status = "failed"
                nodes[node_id].capacity = 0.0  # complete failure
                if hasattr(nodes[node_id], "write_capacity"):
                    nodes[node_id].write_capacity = 0.0
    return events

def run_simulation(graph: CanvasGraph, duration_ticks: int, failures: List[Dict[str, Any]]) -> List[SimulationTickResult]:
    history = []
    G = build_nx_graph(graph)
    
    # Check for cycles
    try:
        topo_order = list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        # Fallback if there are cycles (e.g. retries), process in random order / iterative
        topo_order = list(G.nodes())

    # Deepcopy to mutate state over ticks
    current_state = copy.deepcopy(graph.nodes)

    for tick in range(duration_ticks):
        tick_events = []
        
        # Reset throughput for correct propagation
        for node_id in current_state:
            # ONLY clients generate new load base. Mid-nodes depend on incoming.
            if getattr(current_state[node_id], "type", "") != "client":
                current_state[node_id].throughput = 0.0
                
        tick_events.extend(apply_failures(current_state, tick, failures))

        for node_id in topo_order:
            node = current_state[node_id]
            node_type = getattr(node, "type", "")
            
            # Incoming traffic calc
            incoming_rps = 0.0
            if node_type == "client":
                # Add burst logic optionally
                base_rps = getattr(node, "base_rps", None)
                if base_rps is None: base_rps = 100.0
                burst_factor = getattr(node, "burst_factor", None)
                if burst_factor is None: burst_factor = 1.0
                
                incoming_rps = base_rps * burst_factor
            else:
                incoming_edges = list(G.predecessors(node_id))
                for pred in incoming_edges:
                    pred_successors_count = len(list(G.successors(pred)))
                    split_factor = max(1, pred_successors_count)
                    incoming_rps += current_state[pred].throughput / split_factor
                    
            # M/M/1 and Little's Law Logic (simplified)
            capacity = getattr(node, "capacity", None)
            if capacity is None:
                capacity = 1000.0
                
            if node_type == "database":
                write_cap = getattr(node, "write_capacity", None)
                if write_cap is not None:
                    capacity = write_cap
                else:
                    capacity = 500.0
            
            if node_type == "client":
                node.throughput = incoming_rps
                node.drop_rate = 0.0
                node.status = "healthy"
                b_lat = getattr(node, "base_latency", None)
                node.latency = b_lat if b_lat is not None else 10.0
            elif capacity is None or capacity <= 0:
                node.throughput = 0.0
                node.drop_rate = incoming_rps
                if incoming_rps > 0:
                    node.status = "failed"
            else:
                if incoming_rps > capacity:
                    node.throughput = capacity
                    node.drop_rate = incoming_rps - capacity
                    node.queue_depth += int(node.drop_rate) # accumulation
                    
                    b_lat = getattr(node, "base_latency", None)
                    if b_lat is None: b_lat = 10.0
                    node.latency = b_lat + (node.queue_depth * 0.5)
                    
                    if getattr(node, "type", "") != "client" and getattr(node, "status", "") != "critical":
                        tick_events.append(f"Capacity exceeded at {node_id}")
                    node.status = "critical"
                else:
                    node.throughput = incoming_rps
                    node.drop_rate = 0.0
                    node.queue_depth = max(0, node.queue_depth - int(capacity - incoming_rps))
                    
                    b_lat = getattr(node, "base_latency", None)
                    if b_lat is None: b_lat = 10.0
                    node.latency = b_lat
                    
                    if incoming_rps > capacity * 0.8:
                        node.status = "warning"
                    elif node.status != "failed":
                        node.status = "healthy"
            
        history.append(SimulationTickResult(
            tick=tick,
            nodes=copy.deepcopy(current_state),
            events=tick_events
        ))
        
    return history

import asyncio
import random

async def run_simulation_stream(graph: CanvasGraph, duration_ticks: int, failures: List[Dict[str, Any]], chaos_mode: bool = False):
    G = build_nx_graph(graph)
    
    try:
        topo_order = list(nx.topological_sort(G))
    except nx.NetworkXUnfeasible:
        topo_order = list(G.nodes())

    current_state = copy.deepcopy(graph.nodes)

    for tick in range(duration_ticks):
        tick_events = []
        
        for node_id in current_state:
            if getattr(current_state[node_id], "type", "") != "client":
                current_state[node_id].throughput = 0.0
                
        tick_events.extend(apply_failures(current_state, tick, failures))
        
        # CHAOS MODE: Randomly kill a node every 15 ticks
        if chaos_mode and tick > 0 and tick % 15 == 0:
            targets = [n for n, d in current_state.items() if getattr(d, "type", "") != "client" and getattr(d, "status", "healthy") != "failed"]
            if targets:
                assassinated = random.choice(targets)
                current_state[assassinated].capacity = 0.0
                if hasattr(current_state[assassinated], "write_capacity"):
                    current_state[assassinated].write_capacity = 0.0
                current_state[assassinated].status = "failed"
                tick_events.append(f"CHAOS DAEMON struck! {assassinated} eradicated.")

        for node_id in topo_order:
            node = current_state[node_id]
            node_type = getattr(node, "type", "")
            
            incoming_rps = 0.0
            if node_type == "client":
                base_rps = getattr(node, "base_rps", None)
                if base_rps is None: base_rps = 100.0
                burst_factor = getattr(node, "burst_factor", None)
                if burst_factor is None: burst_factor = 1.0
                incoming_rps = base_rps * burst_factor
            else:
                incoming_edges = list(G.predecessors(node_id))
                for pred in incoming_edges:
                    pred_successors_count = len(list(G.successors(pred)))
                    split_factor = max(1, pred_successors_count)
                    incoming_rps += current_state[pred].throughput / split_factor
                    
            capacity = getattr(node, "capacity", None)
            if capacity is None: capacity = 1000.0
                
            if node_type == "database":
                write_cap = getattr(node, "write_capacity", None)
                if write_cap is not None: capacity = write_cap
                else: capacity = 500.0
            
            if node_type == "client":
                node.throughput = incoming_rps
                node.drop_rate = 0.0
                node.status = "healthy"
                b_lat = getattr(node, "base_latency", None)
                node.latency = b_lat if b_lat is not None else 10.0
            elif capacity is None or capacity <= 0:
                node.throughput = 0.0
                node.drop_rate = incoming_rps
                if incoming_rps > 0:
                    node.status = "failed"
            else:
                if incoming_rps > capacity:
                    node.throughput = capacity
                    node.drop_rate = incoming_rps - capacity
                    node.queue_depth += int(node.drop_rate)
                    
                    b_lat = getattr(node, "base_latency", None)
                    if b_lat is None: b_lat = 10.0
                    node.latency = b_lat + (node.queue_depth * 0.5)
                    
                    if getattr(node, "type", "") != "client" and getattr(node, "status", "") != "critical":
                        tick_events.append(f"Capacity exceeded at {node_id}")
                    node.status = "critical"
                else:
                    node.throughput = incoming_rps
                    node.drop_rate = 0.0
                    node.queue_depth = max(0, node.queue_depth - int(capacity - incoming_rps))
                    
                    b_lat = getattr(node, "base_latency", None)
                    if b_lat is None: b_lat = 10.0
                    node.latency = b_lat
                    
                    if incoming_rps > capacity * 0.8:
                        node.status = "warning"
                    elif node.status != "failed":
                        node.status = "healthy"
            
        result = SimulationTickResult(
            tick=tick,
            nodes=copy.deepcopy(current_state),
            events=tick_events
        )
        yield result
        await asyncio.sleep(0.05)  # 50ms pulse for visually beautiful streaming

