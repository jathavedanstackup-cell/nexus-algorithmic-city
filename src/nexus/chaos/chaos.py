"""Chaos Mode: composes simultaneous failures against the city's own
assumptions (fires+floods, closures, demand spikes, resource shortages,
isolated zones, emergency conflicts). Deterministic under a seed, and must
never raise on infeasible input -- it reports graceful degradation instead.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from nexus.algorithms.traversal import dfs_components
from nexus.city.city import City
from nexus.emergency.dispatch import run_dispatch
from nexus.events import events as ev


@dataclass
class ChaosReport:
    seed: int
    actions: list[str]
    incidents_triggered: list[str]
    dispatch_outcomes: list[dict]
    components_after: int
    isolated_zones: list[str]
    graceful_failures: list[str]
    survived: bool


def run_chaos(city: City, seed: int = 42, intensity: int = 4) -> ChaosReport:
    rng = random.Random(seed)
    actions: list[str] = []
    incidents: list[str] = []
    dispatch_outcomes: list[dict] = []
    graceful_failures: list[str] = []

    zones: list[str] = sorted({str(city.graph.node_attrs(n).get("zone")) for n in city.graph.nodes()})
    nodes = list(city.graph.nodes())

    for step in range(intensity):
        choice = rng.choice(["fire", "flood", "road_failure", "power_failure", "demand_spike"])
        try:
            if choice == "fire":
                zone = rng.choice(zones)
                res = ev.trigger_fire(city, zone, rng)
                incidents.append(res.incident_id)
                actions.append(f"chaos[{step}] fire in {zone} -> {res.incident_id}")
            elif choice == "flood":
                zone = rng.choice(zones)
                res = ev.trigger_flood(city, zone, rng)
                incidents.append(res.incident_id)
                actions.append(f"chaos[{step}] flood in {zone} closed {len(res.closed_edges)} roads")
            elif choice == "road_failure":
                u = rng.choice(nodes)
                neighbors = list(city.graph.neighbors(u))
                if neighbors:
                    v = rng.choice(neighbors).to
                    res = ev.trigger_road_failure(city, u, v, rng=rng)
                    actions.append(f"chaos[{step}] road failure {u}<->{v}")
                else:
                    graceful_failures.append(f"chaos[{step}] road_failure skipped: {u} has no active edges")
            elif choice == "power_failure":
                zone = rng.choice(zones)
                res = ev.trigger_power_failure(city, zone, rng=rng)
                actions.append(f"chaos[{step}] power failure in {zone}")
            elif choice == "demand_spike":
                # Simulate a demand spike by marking several idle units busy.
                idle = [unit for unit in city.vehicles.values() if unit.status == "idle"]
                spike_count = min(len(idle), rng.randint(1, 3))
                for unit in idle[:spike_count]:
                    unit.status = "dispatched"
                actions.append(f"chaos[{step}] demand spike consumed {spike_count} units")
        except Exception as exc:  # noqa: BLE001 - chaos must degrade gracefully
            graceful_failures.append(f"chaos[{step}] {choice} failed gracefully: {exc}")

    # Try to dispatch to every triggered incident; failures are recorded, not raised.
    for inc_id in incidents:
        try:
            result = run_dispatch(city, inc_id)
            dispatch_outcomes.append({
                "incident_id": inc_id,
                "dispatched_unit": result.dispatched_unit,
                "candidates": len(result.candidates),
            })
            if result.dispatched_unit is None:
                graceful_failures.append(f"no unit could reach {inc_id} (isolated or resource-exhausted)")
        except Exception as exc:  # noqa: BLE001
            graceful_failures.append(f"dispatch to {inc_id} failed gracefully: {exc}")

    components = dfs_components(city.graph)
    isolated = [f"component_{i}" for i, c in enumerate(components) if len(c) < 3]

    return ChaosReport(
        seed=seed,
        actions=actions,
        incidents_triggered=incidents,
        dispatch_outcomes=dispatch_outcomes,
        components_after=len(components),
        isolated_zones=isolated,
        graceful_failures=graceful_failures,
        survived=True,
    )
