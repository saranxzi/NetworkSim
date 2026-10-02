"""WebSocket streaming tests: payload validation, plugins, load profiles."""
import json

from starlette.websockets import WebSocketDisconnect

MINI_GRAPH = {
    "nodes": {
        "c1": {"label": "Client", "type": "client", "base_rps": 100.0, "burst_factor": 1.0},
        "api": {"label": "API", "type": "api_server", "capacity": 1000.0, "base_latency": 10.0},
        "db": {"label": "DB", "type": "database", "write_capacity": 1000.0, "read_capacity": 1000.0, "base_latency": 20.0},
    },
    "edges": [
        {"source": "c1", "target": "api"},
        {"source": "api", "target": "db"},
    ],
}


def _drain(ws):
    """Collect all tick messages until the server closes."""
    ticks = []
    while True:
        try:
            ticks.append(json.loads(ws.receive_text()))
        except WebSocketDisconnect:
            return ticks


def _expect_close(ws) -> WebSocketDisconnect:
    """Read until the server closes and return the disconnect exception."""
    while True:
        try:
            ws.receive_text()
        except WebSocketDisconnect as exc:
            return exc


def test_ws_streams_ticks(client):
    with client.websocket_connect("/ws/simulate") as ws:
        ws.send_text(json.dumps({"graph": MINI_GRAPH, "duration_ticks": 2, "seed": 0}))
        ticks = _drain(ws)

    assert [t["tick"] for t in ticks] == [0, 1]
    assert ticks[0]["nodes"]["api"]["throughput"] == 100.0


def test_ws_invalid_seed_closes_with_policy_code(client):
    with client.websocket_connect("/ws/simulate") as ws:
        ws.send_text(json.dumps({"graph": MINI_GRAPH, "duration_ticks": 2, "seed": "not-a-number"}))
        code = _expect_close(ws).code
    assert code == 1007


def test_ws_applies_plugins(client):
    plugin = (
        "def on_tick(state, incoming_rps):\n"
        "    return {'forwarded': incoming_rps * 0.5, 'dropped': incoming_rps * 0.5}\n"
    )
    payload = {
        "graph": MINI_GRAPH,
        "duration_ticks": 1,
        "seed": 0,
        "plugins": {"api_server": plugin},
    }
    with client.websocket_connect("/ws/simulate") as ws:
        ws.send_text(json.dumps(payload))
        ticks = _drain(ws)

    assert ticks[0]["nodes"]["api"]["throughput"] == 50.0
    assert ticks[0]["nodes"]["db"]["throughput"] == 50.0


def test_ws_applies_load_profile(client):
    payload = {
        "graph": MINI_GRAPH,
        "duration_ticks": 2,
        "seed": 0,
        "load_profile": {"type": "soak", "params": {"constant_rps": 250.0}},
    }
    with client.websocket_connect("/ws/simulate") as ws:
        ws.send_text(json.dumps(payload))
        ticks = _drain(ws)

    assert ticks[0]["nodes"]["api"]["throughput"] == 250.0


def test_ws_rejects_oversized_node_count(client):
    nodes = {
        f"n{i}": {"label": f"n{i}", "type": "api_server", "capacity": 100.0}
        for i in range(201)
    }
    with client.websocket_connect("/ws/simulate") as ws:
        ws.send_text(json.dumps({"graph": {"nodes": nodes, "edges": []}, "duration_ticks": 1}))
        code = _expect_close(ws).code
    assert code == 1008
