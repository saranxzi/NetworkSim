import pytest
from networksim.engine.graph import SimGraph

def test_simgraph_dag_ordering():
    node_ids = ["client", "lb", "api", "db"]
    edges = [("client", "lb"), ("lb", "api"), ("api", "db")]
    graph = SimGraph(node_ids, edges)

    assert graph.topo_order == ["client", "lb", "api", "db"]
    assert graph.predecessors("lb") == ["client"]
    assert graph.successors("lb") == ["api"]
    assert graph.predecessors("client") == []
    assert graph.successors("db") == []

def test_simgraph_branching():
    node_ids = ["client", "lb", "api1", "api2", "db"]
    edges = [
        ("client", "lb"),
        ("lb", "api1"),
        ("lb", "api2"),
        ("api1", "db"),
        ("api2", "db")
    ]
    graph = SimGraph(node_ids, edges)

    assert set(graph.successors("lb")) == {"api1", "api2"}
    assert set(graph.predecessors("db")) == {"api1", "api2"}
    assert graph.topo_order.index("client") < graph.topo_order.index("lb")
    assert graph.topo_order.index("lb") < graph.topo_order.index("api1")
    assert graph.topo_order.index("api1") < graph.topo_order.index("db")

def test_simgraph_cycle_fallback():
    node_ids = ["a", "b", "c"]
    edges = [("a", "b"), ("b", "c"), ("c", "a")]
    graph = SimGraph(node_ids, edges)

    # Should not throw exception and should contain all nodes in topo_order
    assert set(graph.topo_order) == {"a", "b", "c"}
    assert graph.predecessors("a") == ["c"]
    assert graph.successors("a") == ["b"]

def test_simgraph_cycle_fallback_keeps_disconnected_nodes():
    node_ids = ["a", "b", "c", "x", "y"]
    edges = [("a", "b"), ("b", "c"), ("c", "a"), ("x", "y")]
    graph = SimGraph(node_ids, edges)

    # BFS from a single vertex would drop the second component
    assert set(graph.topo_order) == {"a", "b", "c", "x", "y"}

def test_simgraph_unknown_edge_raises_clear_error():
    with pytest.raises(KeyError):
        SimGraph(["a"], [("a", "ghost")])
