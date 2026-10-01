"""Simulator-level behavior tests: fresh run state, failure injection, plugins."""
import pytest
from networksim.models import (
    CanvasGraph, ClientData, ApiServerData, DatabaseData, Edge,
)
from networksim.engine.simulator import NetworkSimulator


def _chain_graph(api_status="healthy", api_throughput=0.0):
    nodes = {
        "c1": ClientData(label="Client", base_rps=100.0),
        "api": ApiServerData(
            label="API",
            capacity=200.0,
            base_latency=10.0,
            status=api_status,
            throughput=api_throughput,
            queue_depth=42,
            drop_rate=7.0,
            latency=99.0,
        ),
    }
    edges = [Edge(source="c1", target="api")]
    return CanvasGraph(nodes=nodes, edges=edges)


def test_stale_runtime_state_is_reset():
    """Runtime telemetry left in the payload must not leak into a new run."""
    sim = NetworkSimulator(_chain_graph(api_status="failed", api_throughput=123.0),
                           duration_ticks=1, failures=[], seed=0)
    tick0 = sim.run_sync()[0]

    assert tick0["nodes"]["api"]["status"] == "healthy"
    assert tick0["nodes"]["api"]["throughput"] == 100.0
    assert tick0["nodes"]["api"]["queue_depth"] == 0
    assert tick0["nodes"]["api"]["drop_rate"] == 0.0
    assert tick0["nodes"]["api"]["latency"] == 10.0


def test_client_failure_injection_is_ignored_once():
    """A failure injected on a client node must not re-fire every tick."""
    failures = [{"node_id": "c1", "start_tick": 0, "end_tick": 5}]
    sim = NetworkSimulator(_chain_graph(), duration_ticks=4, failures=failures, seed=0)
    ticks = sim.run_sync()

    injected = [e for t in ticks for e in t["events"] if "Injected failure" in e]
    assert len(injected) == 0
    # Client keeps generating traffic despite the injected failure
    assert all(t["nodes"]["c1"]["throughput"] == 100.0 for t in ticks if "throughput" in t["nodes"].get("c1", {}))


def test_plugin_registry_affects_flow():
    from networksim.plugins.registry import PluginRegistry

    nodes = {
        "c1": ClientData(label="Client", base_rps=200.0),
        "api": ApiServerData(label="API", capacity=1000.0, base_latency=10.0),
        "db": DatabaseData(label="DB", write_capacity=1000.0, read_capacity=1000.0, base_latency=20.0),
    }
    edges = [
        Edge(source="c1", target="api"),
        Edge(source="api", target="db"),
    ]
    graph = CanvasGraph(nodes=nodes, edges=edges)

    registry = PluginRegistry()
    registry.register("api_server", '''
def on_tick(state, incoming_rps):
    forwarded = incoming_rps * 0.5
    return {"forwarded": forwarded, "dropped": incoming_rps - forwarded}
''')

    sim = NetworkSimulator(graph, duration_ticks=1, failures=[], seed=0, plugin_registry=registry)
    tick0 = sim.run_sync()[0]

    assert tick0["nodes"]["api"]["throughput"] == 100.0
    assert tick0["nodes"]["db"]["throughput"] == 100.0


def test_load_profile_drives_client_traffic():
    nodes = {
        "c1": ClientData(label="Client", base_rps=100.0),
        "api": ApiServerData(label="API", capacity=10000.0, base_latency=10.0),
    }
    graph = CanvasGraph(nodes=nodes, edges=[Edge(source="c1", target="api")])
    profile = {"type": "ramp", "params": {"start_rps": 100.0, "peak_rps": 500.0, "ramp_ticks": 4}}
    sim = NetworkSimulator(graph, duration_ticks=5, failures=[], seed=0,
                           load_profile=profile)
    api_rps = [t["nodes"]["api"]["throughput"] for t in sim.run_sync()]
    assert api_rps == [100.0, 200.0, 300.0, 400.0, 500.0]


def test_load_profile_scales_clients_proportionally():
    nodes = {
        "c_big": ClientData(label="Big", base_rps=300.0),
        "c_small": ClientData(label="Small", base_rps=100.0),
        "api": ApiServerData(label="API", capacity=100000.0, base_latency=10.0),
    }
    edges = [
        Edge(source="c_big", target="api"),
        Edge(source="c_small", target="api"),
    ]
    graph = CanvasGraph(nodes=nodes, edges=edges)
    profile = {"type": "soak", "params": {"constant_rps": 400.0}}

    sim = NetworkSimulator(graph, duration_ticks=1, failures=[], seed=0, load_profile=profile)
    tick0 = sim.run_sync()[0]

    assert tick0["nodes"]["c_big"]["throughput"] == 300.0
    assert tick0["nodes"]["c_small"]["throughput"] == 100.0


def test_malformed_load_profile_is_ignored():
    sim = NetworkSimulator(_chain_graph(), duration_ticks=1, failures=[], seed=0,
                           load_profile={"type": "nonsense", "params": {}})
    tick0 = sim.run_sync()[0]
    assert tick0["nodes"]["api"]["throughput"] == 100.0
