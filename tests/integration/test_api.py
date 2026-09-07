from fastapi.testclient import TestClient

from nexus.api.app import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_simulation_and_get_city():
    r = client.post("/api/v1/simulations", json={"profile": "small", "seed": 7})
    assert r.status_code == 200
    sim_id = r.json()["simulation_id"]

    r2 = client.get(f"/api/v1/city?simulation_id={sim_id}")
    assert r2.status_code == 200
    assert r2.json()["city"]["num_nodes"] > 0


def test_post_event_and_timeline():
    r = client.post("/api/v1/simulations", json={"profile": "small", "seed": 8})
    sim_id = r.json()["simulation_id"]
    r2 = client.post(f"/api/v1/simulations/{sim_id}/events", json={"kind": "fire", "zone": "industrial_1"})
    assert r2.status_code == 200
    r3 = client.get(f"/api/v1/simulations/{sim_id}/timeline")
    assert len(r3.json()["timeline"]) >= 1


def test_route_endpoint_agrees_on_cost():
    r = client.post("/api/v1/simulations", json={"profile": "small", "seed": 9})
    sim_id = r.json()["simulation_id"]
    # grab two node ids indirectly via a benchmark run on same profile/seed
    from nexus.city.city import City
    city = City(profile="small", seed=9)
    nodes = list(city.graph.nodes())
    r2 = client.post("/api/v1/routes", json={
        "simulation_id": sim_id, "start": nodes[0], "goal": nodes[-1], "algorithm": "astar"
    })
    assert r2.status_code == 200
    body = r2.json()
    if body["dijkstra"]["found"]:
        assert body["agree_on_cost"] is True


def test_evacuation_endpoint_known_graph():
    r = client.post("/api/v1/evacuation", json={"scenario": "bridge_closure"})
    assert r.status_code == 200
    body = r.json()
    assert body["max_flow"] < 15  # bridge closure reduces the known max flow of 15


def test_benchmark_endpoint_small_profile():
    r = client.post("/api/v1/benchmarks", json={"profile": "small", "seed": 42, "algorithms": ["dijkstra", "astar"]})
    assert r.status_code == 200
    records = r.json()["records"]
    assert len(records) == 2
    assert all(rec["runtime_ms"] >= 0 for rec in records)


def test_metrics_endpoint():
    r = client.get("/api/v1/metrics")
    assert r.status_code == 200
    assert "uptime_seconds" in r.json()


def test_route_unknown_node_returns_400():
    r = client.post("/api/v1/routes", json={"start": "does_not_exist", "goal": "also_missing"})
    assert r.status_code == 400
