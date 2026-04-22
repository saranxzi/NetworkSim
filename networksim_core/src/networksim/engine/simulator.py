"""Main simulator orchestration."""
import asyncio
import random
from typing import Dict, Any, List, AsyncGenerator, Optional
from networksim.models import CanvasGraph
from networksim.engine.graph import SimGraph
from networksim.engine.physics import NodeState, evaluate_node_physics
from networksim.engine.delta import DeltaTracker
from networksim.engine.chaos import ChaosEngine

class NetworkSimulator:
    """
    Core simulation engine. Async generator that yields tick results.
    
    Used identically by:
    - FastAPI WebSocket handler (async for tick in simulator.run(): ...)
    - CLI runner (simulator.run_sync())
    
    Determinism guarantee: Given the same seed, graph, failures, and
    load profile, the output is byte-identical across runs.
    """
    
    def __init__(self, graph: CanvasGraph, duration_ticks: int, failures: List[Dict[str, Any]], chaos_mode: bool = False, seed: int = 0, plugin_registry=None):
        self.plugin_registry = plugin_registry
        node_ids = list(graph.nodes.keys())
        edges = [(edge.source, edge.target) for edge in graph.edges]
        self.graph = SimGraph(node_ids, edges)
        
        self.state: Dict[str, NodeState] = {
            nid: NodeState.from_pydantic(nid, model)
            for nid, model in graph.nodes.items()
        }
        
        self.duration_ticks = duration_ticks
        self.failures = failures
        self.chaos_mode = chaos_mode
        
        self.rng = random.Random(seed)
        self.delta_tracker = DeltaTracker(node_ids)
        self.chaos_engine = ChaosEngine(self.rng) if chaos_mode else None
        
    def _step(self, tick: int) -> List[str]:
        """Perform physics, failure, chaos, and plugin processing for a single tick."""
        events: List[str] = []
        
        # 1. Apply scheduled failure injections
        for f in self.failures:
            start = f.get("start_tick", 0)
            end = f.get("end_tick", 999999)
            if start <= tick <= end:
                nid = f.get("node_id")
                if nid in self.state and self.state[nid].status != "failed":
                    self.state[nid].status = "failed"
                    self.state[nid].capacity = 0.0
                    events.append(f"Injected failure at {nid}")
        
        # 2. Apply chaos
        if self.chaos_engine:
            chaos_events = self.chaos_engine.maybe_strike(tick, self.state)
            events.extend(chaos_events)
            
        # 3. Reset non-client throughputs
        for node in self.state.values():
            if node.node_type != "client":
                node.current_rps = 0.0
                
        # 4. Propagate traffic in topological order
        for nid in self.graph.topo_order:
            node = self.state[nid]
            incoming_rps = self._calc_incoming_rps(nid, node)
            evaluate_node_physics(node, incoming_rps, events, nid)
            
            # 4b. Apply plugin override if registered
            if self.plugin_registry and self.plugin_registry.has_plugin(node.node_type):
                try:
                    plugin = self.plugin_registry.get_plugin(node.node_type)
                    plugin_state = {
                        "capacity": node.capacity,
                        "status": node.status,
                        "queue_depth": node.queue_depth,
                        "latency": node.current_latency,
                    }
                    result = plugin.execute_tick(plugin_state, incoming_rps)
                    node.current_rps = result.get("forwarded", node.current_rps)
                    node.drop_rate = result.get("dropped", node.drop_rate)
                except Exception:
                    pass  # Fallback to physics engine result on plugin error
                    
        return events

    async def run(self) -> AsyncGenerator[dict, None]:
        """Async generator yielding one delta-compressed dict per tick."""
        for tick in range(self.duration_ticks):
            events = self._step(tick)
            delta = self.delta_tracker.compute_delta(self.state)
            
            yield {
                "tick": tick,
                "nodes": delta,
                "events": events,
                "full_snapshot": tick == 0
            }
            await asyncio.sleep(0)
            
    def run_sync(self) -> List[dict]:
        """Synchronous version for CLI and tests. Returns all ticks as a list of delta dicts."""
        async def _run():
            return [tick async for tick in self.run()]
        return asyncio.run(_run())

    def run_snapshots(self) -> List[Any]:
        """Synchronous full execution returning a list of SimulationTickResult models."""
        from networksim.models import BaseNodeData, SimulationTickResult
        history = []
        for tick in range(self.duration_ticks):
            events = self._step(tick)
            nodes_snapshot = {
                nid: BaseNodeData(
                    label=node.label,
                    type=node.node_type,
                    status=node.status,
                    throughput=round(node.current_rps, 1),
                    latency=round(node.current_latency, 1),
                    queue_depth=node.queue_depth,
                    drop_rate=round(node.drop_rate, 1),
                    capacity=node.capacity
                )
                for nid, node in self.state.items()
            }
            history.append(SimulationTickResult(
                tick=tick,
                nodes=nodes_snapshot,
                events=events
            ))
        return history

    def _calc_incoming_rps(self, node_id: str, node_state: NodeState) -> float:
        """Calculate incoming traffic for a node, splitting across active successors."""
        if node_state.node_type == "client":
            return node_state.base_rps * node_state.burst_factor
        
        incoming = 0.0
        preds = self.graph.predecessors(node_id)
        for p in preds:
            pred_node = self.state[p]
            succs = self.graph.successors(p)
            # Only split traffic among non-failed successors
            active_succs = [s for s in succs if self.state[s].status != "failed"]
            if node_id in active_succs and len(active_succs) > 0:
                incoming += pred_node.current_rps / len(active_succs)
        return incoming
