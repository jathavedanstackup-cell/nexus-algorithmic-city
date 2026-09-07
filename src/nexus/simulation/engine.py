"""Simulation engine: owns a City instance and an event timeline, providing
the single source of truth the API/CLI operate against. STATE -> EVENT ->
ALGORITHM loop."""
from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from nexus.city.city import City
from nexus.events import events as ev


@dataclass
class TimelineEntry:
    id: str
    timestamp: str
    kind: str
    description: str
    data: dict


class Simulation:
    def __init__(self, sim_id: str, profile: str = "small", seed: int = 42) -> None:
        self.id = sim_id
        self.city = City(profile=profile, seed=seed)
        self.rng = random.Random(seed)
        self.timeline: list[TimelineEntry] = []
        self._log("simulation_started", f"Simulation {sim_id} started (profile={profile}, seed={seed})", {})

    def _log(self, kind: str, description: str, data: dict) -> TimelineEntry:
        entry = TimelineEntry(
            id=f"evt_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(UTC).isoformat(),
            kind=kind,
            description=description,
            data=data,
        )
        self.timeline.append(entry)
        return entry

    def trigger_event(self, kind: str, zone: str | None = None, node_a: str | None = None,
                       node_b: str | None = None) -> TimelineEntry:
        if kind == "fire":
            res = ev.trigger_fire(self.city, zone or "industrial_1", self.rng)
        elif kind == "flood":
            res = ev.trigger_flood(self.city, zone or "north_district", self.rng)
        elif kind == "road_failure":
            if not node_a or not node_b:
                nodes = list(self.city.graph.nodes())
                node_a, node_b = nodes[0], next(self.city.graph.neighbors(nodes[0])).to
            res = ev.trigger_road_failure(self.city, node_a, node_b)
        elif kind == "power_failure":
            res = ev.trigger_power_failure(self.city, zone or "district_7")
        else:
            raise ValueError(f"unknown event kind '{kind}'")
        return self._log(kind, res.description, {
            "incident_id": res.incident_id,
            "affected_nodes": res.affected_nodes,
            "closed_edges": res.closed_edges,
        })

    def snapshot(self) -> dict:
        return {
            "simulation_id": self.id,
            "city": self.city.snapshot(),
            "timeline_length": len(self.timeline),
        }


class SimulationRegistry:
    """In-memory registry (hash-map) of running simulations, keyed by id."""

    def __init__(self) -> None:
        self._sims: dict[str, Simulation] = {}

    def create(self, profile: str = "small", seed: int = 42) -> Simulation:
        sim_id = f"sim_{uuid.uuid4().hex[:8]}"
        sim = Simulation(sim_id, profile=profile, seed=seed)
        self._sims[sim_id] = sim
        return sim

    def get(self, sim_id: str) -> Simulation | None:
        return self._sims.get(sim_id)

    def default(self) -> Simulation:
        """Get-or-create a default simulation so the UI has something to show
        immediately on load."""
        if not self._sims:
            return self.create(profile="medium", seed=42)
        return next(iter(self._sims.values()))


registry = SimulationRegistry()
