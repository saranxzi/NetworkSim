"""Test determinism of the simulation engine."""
import pytest
from networksim.models import CanvasGraph, ClientData, ApiServerData, DatabaseData, Edge
from networksim.engine.simulator import NetworkSimulator

def test_determinism():
    nodes = {
        "client1": ClientData(label="Client", base_rps=100.0, capacity=1000.0),
        "api1": ApiServerData(label="API", capacity=200.0, base_latency=10.0),
        "db1": DatabaseData(label="Database", capacity=50.0, write_capacity=50.0, read_capacity=50.0, base_latency=5.0)
    }
    edges = [
        Edge(source="client1", target="api1"),
        Edge(source="api1", target="db1")
    ]
    graph = CanvasGraph(nodes=nodes, edges=edges)

    sim1 = NetworkSimulator(graph, duration_ticks=30, failures=[], chaos_mode=True, seed=42)
    res1 = sim1.run_sync()

    sim2 = NetworkSimulator(graph, duration_ticks=30, failures=[], chaos_mode=True, seed=42)
    res2 = sim2.run_sync()

    assert res1 == res2

    sim3 = NetworkSimulator(graph, duration_ticks=30, failures=[], chaos_mode=True, seed=99)
    res3 = sim3.run_sync()

    assert res1 != res3
