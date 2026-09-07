"""Emergency response pipeline: the 5-stage dispatch mechanic.

01 Find units (priority queue by distance/availability)
02 Generate routes (A*/Dijkstra)
03 Rank (severity + ETA)
04 Dispatch (best candidate)
05 Recalculate (dynamic graph, e.g. if a road closes mid-response)
"""
from __future__ import annotations

from dataclasses import dataclass

from nexus.algorithms.routing import RouteResult, astar, dijkstra
from nexus.city.city import City
from nexus.structures.heap import PriorityQueue


@dataclass
class Candidate:
    unit_id: str
    route: RouteResult
    eta: float
    rank_score: float


@dataclass
class DispatchResult:
    incident_id: str
    stage_log: list[str]
    candidates: list[Candidate]
    dispatched_unit: str | None
    route: RouteResult | None
    telemetry: dict


def run_dispatch(city: City, incident_id: str, algorithm: str = "astar") -> DispatchResult:
    incident = city.incidents.get(incident_id)
    if incident is None:
        raise ValueError(f"unknown incident {incident_id}")

    log: list[str] = []
    route_fn = astar if algorithm == "astar" else dijkstra

    # 01 Find units: priority queue of idle units ordered by (placeholder)
    # straight distance proxy so we explore closest-first.
    pq: PriorityQueue[str] = PriorityQueue()
    idle_units = [v for v in city.vehicles.values() if v.status == "idle"]
    for v in idle_units:
        pq.push(0.0, v.id)  # true ranking happens after routing (stage 3)
    log.append(f"01 find_units: {len(idle_units)} idle units in priority queue")

    # 02 Generate routes for each idle unit -> incident node
    candidates: list[Candidate] = []
    total_nodes_explored = 0
    while not pq.is_empty():
        unit_id = pq.pop()
        unit = city.vehicles.get(unit_id)
        if unit is None:
            continue
        route = route_fn(city.graph, unit.location, incident.node)
        total_nodes_explored += route.nodes_explored
        if not route.found:
            continue
        eta = route.cost  # weight units modeled as time
        rank_score = incident.severity * 100 - eta
        candidates.append(Candidate(unit_id, route, eta, rank_score))
    log.append(f"02 generate_routes: {len(candidates)} feasible routes computed via {algorithm}")

    # 03 Rank by severity + ETA (higher is better)
    candidates.sort(key=lambda c: c.rank_score, reverse=True)
    log.append("03 rank: candidates sorted by severity-weighted ETA score")

    # 04 Dispatch best candidate
    dispatched_unit = None
    chosen_route = None
    if candidates:
        best = candidates[0]
        best_unit = city.vehicles.get(best.unit_id)
        if best_unit is not None:
            best_unit.status = "dispatched"
        dispatched_unit = best.unit_id
        chosen_route = best.route
        log.append(f"04 dispatch: unit {best.unit_id} dispatched, ETA {best.eta:.2f}")
    else:
        log.append("04 dispatch: no available unit could reach the incident")

    # 05 Recalculate placeholder: exposed for callers to invoke again after a
    # road closes mid-response (see recalculate()).
    log.append("05 recalculate: pipeline ready to recompute if graph changes")

    telemetry = {
        "nodes_explored_total": total_nodes_explored,
        "candidates_considered": len(candidates),
        "algorithm": algorithm,
        "runtime_ms": sum(c.route.runtime_ms for c in candidates),
    }

    return DispatchResult(
        incident_id=incident_id,
        stage_log=log,
        candidates=candidates,
        dispatched_unit=dispatched_unit,
        route=chosen_route,
        telemetry=telemetry,
    )


def recalculate(city: City, unit_id: str, incident_id: str, algorithm: str = "astar") -> RouteResult:
    """Stage 05: recompute a unit's route, e.g. after a road closure."""
    unit = city.vehicles.get(unit_id)
    incident = city.incidents.get(incident_id)
    if unit is None or incident is None:
        raise ValueError(f"unknown unit '{unit_id}' or incident '{incident_id}'")
    route_fn = astar if algorithm == "astar" else dijkstra
    return route_fn(city.graph, unit.location, incident.node)
