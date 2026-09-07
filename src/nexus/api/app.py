"""FastAPI application: Web UI -> REST API -> Algorithm Core boundary."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from nexus.algorithms.routing import astar, dijkstra
from nexus.benchmarking.runner import run_benchmark, write_results
from nexus.chaos.chaos import run_chaos
from nexus.city.city import PROFILES
from nexus.emergency.dispatch import run_dispatch
from nexus.evacuation.evacuation import run_evacuation
from nexus.metrics.metrics import metrics_store
from nexus.simulation.engine import registry

app = FastAPI(title="NEXUS API", version="0.1.0", description="Algorithmic Living City")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class SimulationCreate(BaseModel):
    profile: str = "medium"
    seed: int = 42


class EventCreate(BaseModel):
    kind: str
    zone: str | None = None
    node_a: str | None = None
    node_b: str | None = None


class RouteRequest(BaseModel):
    simulation_id: str | None = None
    start: str
    goal: str
    algorithm: str = "astar"


class EvacuationRequest(BaseModel):
    simulation_id: str | None = None
    scenario: str = "bridge_closure"
    source: str = "A"
    sink: str = "EXIT"


class BenchmarkRequest(BaseModel):
    profile: str = "small"
    seed: int = 42
    algorithms: list[str] = ["dijkstra", "astar"]


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# City / simulation
# ---------------------------------------------------------------------------
@app.get("/api/v1/city")
def get_city(simulation_id: str | None = None):
    sim = registry.get(simulation_id) if simulation_id else registry.default()
    if sim is None:
        raise HTTPException(404, "simulation not found")
    return sim.snapshot()


@app.post("/api/v1/simulations")
def create_simulation(body: SimulationCreate):
    if body.profile not in PROFILES:
        raise HTTPException(400, f"unknown profile, choose from {list(PROFILES)}")
    sim = registry.create(profile=body.profile, seed=body.seed)
    return sim.snapshot()


@app.post("/api/v1/simulations/{sim_id}/events")
def post_event(sim_id: str, body: EventCreate):
    sim = registry.get(sim_id)
    if sim is None:
        raise HTTPException(404, "simulation not found")
    try:
        entry = sim.trigger_event(body.kind, zone=body.zone, node_a=body.node_a, node_b=body.node_b)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return {"event": entry.__dict__, "city": sim.city.snapshot()}


@app.get("/api/v1/simulations/{sim_id}/timeline")
def get_timeline(sim_id: str):
    sim = registry.get(sim_id)
    if sim is None:
        raise HTTPException(404, "simulation not found")
    return {"timeline": [e.__dict__ for e in sim.timeline]}


@app.get("/api/v1/simulations/{sim_id}/dispatch/{incident_id}")
def get_dispatch(sim_id: str, incident_id: str, algorithm: str = "astar"):
    sim = registry.get(sim_id)
    if sim is None:
        raise HTTPException(404, "simulation not found")
    try:
        result = run_dispatch(sim.city, incident_id, algorithm=algorithm)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    metrics_store.dispatch_calls += 1
    return {
        "incident_id": result.incident_id,
        "stage_log": result.stage_log,
        "dispatched_unit": result.dispatched_unit,
        "route": result.route.__dict__ if result.route else None,
        "telemetry": result.telemetry,
        "candidates": [
            {"unit_id": c.unit_id, "eta": c.eta, "rank_score": c.rank_score} for c in result.candidates
        ],
    }


# ---------------------------------------------------------------------------
# Routing / Arena
# ---------------------------------------------------------------------------
@app.post("/api/v1/routes")
def post_route(body: RouteRequest):
    sim = registry.get(body.simulation_id) if body.simulation_id else registry.default()
    if sim is None:
        raise HTTPException(404, "simulation not found")
    graph = sim.city.graph
    if not graph.has_node(body.start) or not graph.has_node(body.goal):
        raise HTTPException(400, "start/goal node not found in city graph")

    dijkstra_result = dijkstra(graph, body.start, body.goal)
    astar_result = astar(graph, body.start, body.goal)
    metrics_store.record_route("dijkstra", dijkstra_result.runtime_ms)
    metrics_store.record_route("astar", astar_result.runtime_ms)

    return {
        "requested_algorithm": body.algorithm,
        "dijkstra": dijkstra_result.__dict__,
        "astar": astar_result.__dict__,
        "agree_on_cost": abs(dijkstra_result.cost - astar_result.cost) < 1e-6 if dijkstra_result.found and astar_result.found else False,
    }


# ---------------------------------------------------------------------------
# Evacuation
# ---------------------------------------------------------------------------
@app.post("/api/v1/evacuation")
def post_evacuation(body: EvacuationRequest):
    sim = registry.get(body.simulation_id) if body.simulation_id else None
    city = sim.city if sim else None
    report = run_evacuation(city, body.scenario, source=body.source, sink=body.sink)
    metrics_store.evacuation_calls += 1
    return {
        "scenario": report.scenario,
        "max_flow": report.max_flow,
        "bottleneck_edge": report.bottleneck_edge,
        "critical_cut": report.critical_cut,
        "at_risk_population": report.at_risk_population,
        "reachable_from_source": report.result.reachable_from_source,
    }


# ---------------------------------------------------------------------------
# Chaos
# ---------------------------------------------------------------------------
@app.post("/api/v1/chaos")
def post_chaos(seed: int = 42, simulation_id: str | None = None, intensity: int = 4):
    sim = registry.get(simulation_id) if simulation_id else registry.default()
    if sim is None:
        raise HTTPException(404, "simulation not found")
    report = run_chaos(sim.city, seed=seed, intensity=intensity)
    return report.__dict__


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------
@app.post("/api/v1/benchmarks")
def post_benchmark(body: BenchmarkRequest):
    if body.profile not in PROFILES:
        raise HTTPException(400, f"unknown profile, choose from {list(PROFILES)}")
    records = run_benchmark(body.profile, seed=body.seed, algorithms=tuple(body.algorithms))
    write_results(records)
    metrics_store.benchmark_runs += 1
    return {"records": [r.__dict__ for r in records]}


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
@app.get("/api/v1/metrics")
def get_metrics():
    return metrics_store.snapshot()


# ---------------------------------------------------------------------------
# Static frontend (served in production/Docker build)
# ---------------------------------------------------------------------------
_WEB_DIST = Path(__file__).resolve().parents[3] / "web" / "dist"
if _WEB_DIST.exists():
    app.mount("/", StaticFiles(directory=str(_WEB_DIST), html=True), name="web")
