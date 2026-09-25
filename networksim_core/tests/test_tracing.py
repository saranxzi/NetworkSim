import pytest
import random
from networksim.tracing import TraceGenerator

def test_trace_generation_linear():
    gen = TraceGenerator(rng=random.Random(42))
    nodes = {
        "client": {"type": "client", "label": "Client", "latency": 10.0, "status": "healthy"},
        "api": {"type": "api_server", "label": "API", "latency": 25.0, "status": "healthy"},
        "db": {"type": "database", "label": "DB", "latency": 50.0, "status": "healthy"}
    }
    topo_order = ["client", "api", "db"]
    edges = [("client", "api"), ("api", "db")]

    trace = gen.generate_trace(0, nodes, topo_order, edges)
    assert trace is not None
    assert len(trace.trace_id) == 32
    assert trace.root_span.service_name == "client"
    assert len(trace.root_span.children) == 1
    assert trace.root_span.children[0].service_name == "api"
    assert len(trace.root_span.children[0].children) == 1
    assert trace.root_span.children[0].children[0].service_name == "db"

    trace_dict = gen.trace_to_dict(trace)
    assert "trace_id" in trace_dict
    assert "root_span" in trace_dict
    assert trace_dict["root_span"]["duration_ms"] == 10.0

def test_trace_cycle_guard():
    gen = TraceGenerator(rng=random.Random(42))
    # Graph with cycle: a -> b -> c -> a
    nodes = {
        "a": {"type": "api_server", "label": "A", "latency": 10.0, "status": "healthy"},
        "b": {"type": "api_server", "label": "B", "latency": 10.0, "status": "healthy"},
        "c": {"type": "api_server", "label": "C", "latency": 10.0, "status": "healthy"},
    }
    topo_order = ["a", "b", "c"]
    edges = [("a", "b"), ("b", "c"), ("c", "a")]

    # Must complete without RecursionError
    trace = gen.generate_trace(0, nodes, topo_order, edges)
    assert trace is not None
    assert trace.root_span.service_name == "a"
