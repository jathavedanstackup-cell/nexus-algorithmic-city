"""City model: builds a deterministic (seeded) road network graph plus
population/vehicle/incident entities backed by the EntityStore hash map."""
from __future__ import annotations

import random
from dataclasses import dataclass

from nexus.structures.graph import Graph
from nexus.structures.queue import EntityStore

ZONE_NAMES = [
    "downtown", "industrial_1", "north_district", "harbor", "district_7",
    "old_town", "suburbs_east", "suburbs_west", "airport", "university",
]

FACILITY_KINDS = ["station", "hospital", "power_plant", "residential", "commercial"]


@dataclass
class CityProfile:
    name: str
    num_nodes: int
    avg_degree: int = 4


PROFILES: dict[str, CityProfile] = {
    "small": CityProfile("small", 50, 4),
    "medium": CityProfile("medium", 1000, 5),
    "large": CityProfile("large", 10000, 6),
    "stress": CityProfile("stress", 50000, 6),  # documented cap, see docs/complexity
}


@dataclass
class Vehicle:
    id: str
    kind: str
    location: str
    status: str = "idle"


@dataclass
class Incident:
    id: str
    kind: str
    zone: str
    node: str
    severity: float
    status: str = "active"


class City:
    """Owns the road-network Graph plus population/vehicle/incident entities."""

    def __init__(self, profile: str = "small", seed: int = 42) -> None:
        if profile not in PROFILES:
            raise ValueError(f"unknown profile '{profile}', choose from {list(PROFILES)}")
        self.profile = PROFILES[profile]
        self.seed = seed
        self.rng = random.Random(seed)
        self.graph = Graph(directed=False)
        self.population = 0
        self.vehicles: EntityStore[Vehicle] = EntityStore()
        self.incidents: EntityStore[Incident] = EntityStore()
        self.stations: list[str] = []
        self.hospitals: list[str] = []
        self._build_network()
        self._seed_population_and_vehicles()

    # -- construction ---------------------------------------------------------
    def _build_network(self) -> None:
        n = self.profile.num_nodes
        rng = self.rng
        # Place nodes on a rough grid with jitter for a plausible city shape,
        # tagging each with a zone so scenarios can target a district.
        side = max(1, int(n ** 0.5))
        for i in range(n):
            node_id = f"node_{i}"
            zone = ZONE_NAMES[i % len(ZONE_NAMES)]
            x = (i % side) + rng.uniform(-0.3, 0.3)
            y = (i // side) + rng.uniform(-0.3, 0.3)
            kind = FACILITY_KINDS[i % len(FACILITY_KINDS)] if i % 7 == 0 else "residential"
            self.graph.add_node(node_id, zone=zone, x=x, y=y, kind=kind)
            if kind == "station":
                self.stations.append(node_id)
            if kind == "hospital":
                self.hospitals.append(node_id)

        # Ensure connectivity: connect each node to previous node (spanning
        # backbone), then add random extra edges for avg_degree. Edge weight
        # is derived from straight-line node distance (>= distance, via a
        # >=1.0 traffic multiplier) so the coordinate-based A* heuristic
        # stays admissible: h(n) never overestimates the true remaining cost.
        nodes = list(self.graph.nodes())

        def weight_for(u: str, v: str) -> float:
            ua, va = self.graph.node_attrs(u), self.graph.node_attrs(v)
            import math
            dist = math.hypot(ua["x"] - va["x"], ua["y"] - va["y"])
            return round(max(dist, 0.05) * rng.uniform(1.0, 1.8), 3)

        for i in range(1, len(nodes)):
            u, v = nodes[i], nodes[rng.randint(0, i - 1)]
            self.graph.add_edge(u, v, weight=weight_for(u, v), capacity=rng.randint(20, 200))

        extra_edges = int(n * self.profile.avg_degree / 2)
        for _ in range(extra_edges):
            u, v = rng.choice(nodes), rng.choice(nodes)
            if u != v:
                self.graph.add_edge(u, v, weight=weight_for(u, v), capacity=rng.randint(20, 200))

        if not self.stations:
            self.stations = [nodes[0]]
        if not self.hospitals:
            self.hospitals = [nodes[-1]]

    def _seed_population_and_vehicles(self) -> None:
        rng = self.rng
        self.population = sum(rng.randint(50, 500) for _ in self.graph.nodes())
        num_vehicles = max(4, self.profile.num_nodes // 20)
        kinds = ["fire_truck", "ambulance", "police"]
        nodes = list(self.graph.nodes())
        for i in range(num_vehicles):
            station = self.stations[i % len(self.stations)] if self.stations else rng.choice(nodes)
            v = Vehicle(id=f"unit_{i}", kind=kinds[i % len(kinds)], location=station)
            self.vehicles.put(v.id, v)

    # -- accessors --------------------------------------------------------------
    def snapshot(self) -> dict:
        return {
            "profile": self.profile.name,
            "seed": self.seed,
            "population": self.population,
            "num_nodes": self.graph.num_nodes,
            "num_edges": self.graph.num_edges,
            "vehicles": len(self.vehicles),
            "active_incidents": sum(1 for i in self.incidents.values() if i.status == "active"),
            "stations": self.stations,
            "hospitals": self.hospitals,
        }

    def nodes_in_zone(self, zone: str) -> list[str]:
        return [n for n in self.graph.nodes() if self.graph.node_attrs(n).get("zone") == zone]
