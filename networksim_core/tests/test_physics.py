import pytest
from networksim.engine.physics import NodeState, evaluate_node_physics, MAX_QUEUE_DEPTH

def test_client_node_physics():
    node = NodeState(
        id="c1", label="Client", node_type="client",
        capacity=1000.0, base_latency=10.0, base_rps=100.0, burst_factor=1.0
    )
    events = []
    evaluate_node_physics(node, 100.0, events, "c1")
    assert node.current_rps == 100.0
    assert node.status == "healthy"
    assert node.drop_rate == 0.0

def test_failed_node_drops_all():
    node = NodeState(
        id="api1", label="API", node_type="api_server",
        capacity=500.0, base_latency=15.0, base_rps=0.0, burst_factor=1.0,
        status="failed"
    )
    events = []
    evaluate_node_physics(node, 300.0, events, "api1")
    assert node.current_rps == 0.0
    assert node.drop_rate == 300.0

def test_healthy_and_warning_states():
    node = NodeState(
        id="api1", label="API", node_type="api_server",
        capacity=1000.0, base_latency=20.0, base_rps=0.0, burst_factor=1.0
    )
    events = []
    # 500 RPS out of 1000 capacity (< 0.8) -> healthy
    evaluate_node_physics(node, 500.0, events, "api1")
    assert node.status == "healthy"
    assert node.current_rps == 500.0
    assert node.drop_rate == 0.0
    assert node.current_latency == 20.0

    # 850 RPS out of 1000 capacity (>= 0.8) -> warning
    evaluate_node_physics(node, 850.0, events, "api1")
    assert node.status == "warning"
    assert node.current_rps == 850.0

def test_critical_overload_and_queue_buffering():
    node = NodeState(
        id="api1", label="API", node_type="api_server",
        capacity=100.0, base_latency=10.0, base_rps=0.0, burst_factor=1.0
    )
    events = []
    # 150 incoming on 100 capacity -> excess 50 gets queued
    evaluate_node_physics(node, 150.0, events, "api1")
    assert node.status == "critical"
    assert node.current_rps == 100.0
    assert node.queue_depth == 50
    assert node.drop_rate == 0.0
    assert any("Capacity exceeded" in e for e in events)

    # Next tick: traffic drops to 0, node serves remaining 50 backlog and recovers to healthy
    events.clear()
    evaluate_node_physics(node, 0.0, events, "api1")
    assert node.current_rps == 50.0
    assert node.queue_depth == 0
    assert node.status == "healthy"
    assert any("Recovery" in e for e in events)
