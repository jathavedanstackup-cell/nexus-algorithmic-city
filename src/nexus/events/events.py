"""Disaster events that mutate live simulation state: fire, flood, road
failure (edge closure), power failure. Each returns a structured record of
what actually changed so the API/CLI/telemetry can report real effects."""
from __future__ import annotations

import random
import uuid
from dataclasses import dataclass

from nexus.city.city import City, Incident


@dataclass
class EventResult:
    id: str
    kind: str
    zone: str
    affected_nodes: list[str]
    closed_edges: list[tuple]
    incident_id: str
    description: str


def _new_incident(city: City, kind: str, zone: str, node: str, severity: float,
                   rng: random.Random | None = None) -> Incident:
    # Id generation is derived from the scenario's own seeded rng (when given)
    # rather than uuid4, so that `chaos --seed N` (and any seeded event
    # sequence) is byte-for-byte reproducible, including generated ids.
    if rng is not None:
        suffix = f"{rng.getrandbits(32):08x}"
    else:
        suffix = uuid.uuid4().hex[:8]
    inc = Incident(id=f"incident_{suffix}", kind=kind, zone=zone, node=node, severity=severity)
    city.incidents.put(inc.id, inc)
    return inc


def trigger_fire(city: City, zone: str, rng: random.Random) -> EventResult:
    targets = city.nodes_in_zone(zone) or list(city.graph.nodes())
    node = rng.choice(targets)
    inc = _new_incident(city, "fire", zone, node, severity=rng.uniform(0.6, 1.0), rng=rng)
    return EventResult(inc.id, "fire", zone, [node], [], inc.id, f"Fire reported at {node} in {zone}")


def trigger_flood(city: City, zone: str, rng: random.Random) -> EventResult:
    targets = city.nodes_in_zone(zone) or list(city.graph.nodes())
    affected = rng.sample(targets, k=min(3, len(targets)))
    closed = []
    for node in affected:
        for edge in list(city.graph.neighbors(node)):
            if rng.random() < 0.5:
                city.graph.set_edge_active(node, edge.to, False)
                closed.append((node, edge.to))
    inc = _new_incident(city, "flood", zone, affected[0], severity=rng.uniform(0.5, 0.9), rng=rng)
    return EventResult(inc.id, "flood", zone, affected, closed, inc.id, f"Flood in {zone} closed {len(closed)} roads")


def trigger_road_failure(city: City, node_a: str, node_b: str, rng: random.Random | None = None) -> EventResult:
    ok = city.graph.set_edge_active(node_a, node_b, False)
    if not ok:
        raise ValueError(f"no road between {node_a} and {node_b}")
    zone = city.graph.node_attrs(node_a).get("zone", "unknown")
    inc = _new_incident(city, "road_failure", zone, node_a, severity=0.4, rng=rng)
    return EventResult(inc.id, "road_failure", zone, [node_a, node_b], [(node_a, node_b)], inc.id,
                        f"Road closed between {node_a} and {node_b}")


def trigger_power_failure(city: City, zone: str, rng: random.Random | None = None) -> EventResult:
    affected = city.nodes_in_zone(zone) or list(city.graph.nodes())[:5]
    for node in affected:
        city.graph.node_attrs(node)["power"] = "down"
    inc = _new_incident(city, "power_failure", zone, affected[0], severity=0.5, rng=rng)
    return EventResult(inc.id, "power_failure", zone, affected, [], inc.id,
                        f"Power failure in {zone} affecting {len(affected)} nodes")
