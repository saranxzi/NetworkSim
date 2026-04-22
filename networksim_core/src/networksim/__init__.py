"""NetworkSim Core — High-performance distributed systems simulation engine."""
from networksim.engine.simulator import NetworkSimulator
from networksim.engine.graph import SimGraph
from networksim.engine.physics import NodeState, evaluate_node_physics
from networksim.engine.delta import DeltaTracker
from networksim.engine.chaos import ChaosEngine

__version__ = "0.3.0"

def run_simulation(graph, duration_ticks: int = 60, failures: list = None, chaos_mode: bool = False, seed: int = 0):
    """Run simulation and return full SimulationTickResult snapshots."""
    sim = NetworkSimulator(graph, duration_ticks, failures or [], chaos_mode=chaos_mode, seed=seed)
    return sim.run_snapshots()

__all__ = [
    "NetworkSimulator",
    "SimGraph",
    "NodeState",
    "evaluate_node_physics",
    "DeltaTracker",
    "ChaosEngine",
    "run_simulation",
]
