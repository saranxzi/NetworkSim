"""Blueprint persistence tests: create, version round-trip, list summary."""
GRAPH_SCHEMA = {
    "nodes": {"c1": {"label": "Client", "type": "client", "base_rps": 100.0}},
    "edges": [],
}


def test_blueprint_version_round_trip(client):
    # Create blueprint
    res = client.post("/api/blueprints", json={"name": "My Topology"})
    assert res.status_code == 200, res.text
    blueprint = res.json()
    bp_id = blueprint["id"]

    # Save a version with a graph
    res = client.post(
        f"/api/blueprints/{bp_id}/versions",
        json={"graph_schema": GRAPH_SCHEMA, "invariants": {"latency < 100": "critical"}},
    )
    assert res.status_code == 200, res.text
    version = res.json()
    assert version["version_number"] == 1
    assert version["graph_schema"] == GRAPH_SCHEMA

    # Detail endpoint returns the latest version with its graph
    res = client.get(f"/api/blueprints/{bp_id}")
    assert res.status_code == 200, res.text
    detail = res.json()
    assert detail["latest_version"]["graph_schema"] == GRAPH_SCHEMA

    # List endpoint includes a version count and timestamps
    res = client.get("/api/blueprints")
    assert res.status_code == 200, res.text
    listed = {b["id"]: b for b in res.json()}
    assert bp_id in listed
    assert listed[bp_id]["version_count"] == 1
    assert listed[bp_id]["updated_at"]


def test_blueprint_not_found(client):
    res = client.get("/api/blueprints/does-not-exist")
    assert res.status_code == 404


def test_blueprint_belongs_to_workspace(client):
    res = client.post("/api/blueprints", json={"name": "Other"})
    other_id = res.json()["id"]

    res = client.post(
        f"/api/blueprints/{other_id}/versions",
        json={"graph_schema": GRAPH_SCHEMA},
    )
    assert res.status_code == 200

    res = client.get(f"/api/blueprints/{other_id}/versions")
    assert res.status_code == 200
    versions = res.json()
    assert len(versions) == 1
    assert versions[0]["version_number"] == 1
