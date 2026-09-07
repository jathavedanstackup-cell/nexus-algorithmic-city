"""Explicit adjacency-list graph implementation used across NEXUS.

This is a from-scratch implementation (no networkx) so the simulation's
mechanics are transparent and testable. networkx may only be used inside
tests as an independent cross-check.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass
class Edge:
    to: str
    weight: float = 1.0
    capacity: float | None = None
    active: bool = True
    id: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            self.id = f"->{self.to}:{self.weight}"


class Graph:
    """Directed, weighted adjacency-list graph with V/E accounting.

    Supports "soft delete" of edges/nodes (active=False) so a running
    simulation can close a road without losing history, which is what the
    dynamic-recalculation and chaos scenarios need.
    """

    def __init__(self, directed: bool = False) -> None:
        self.directed = directed
        self._adj: dict[str, list[Edge]] = {}
        self._nodes: dict[str, dict] = {}

    # -- node/edge management -------------------------------------------------
    def add_node(self, node_id: str, **attrs) -> None:
        if node_id not in self._adj:
            self._adj[node_id] = []
            self._nodes[node_id] = attrs
        else:
            self._nodes[node_id].update(attrs)

    def has_node(self, node_id: str) -> bool:
        return node_id in self._adj

    def node_attrs(self, node_id: str) -> dict:
        return self._nodes[node_id]

    def add_edge(self, u: str, v: str, weight: float = 1.0, capacity: float | None = None) -> None:
        self.add_node(u)
        self.add_node(v)
        self._adj[u].append(Edge(to=v, weight=weight, capacity=capacity))
        if not self.directed:
            self._adj[v].append(Edge(to=u, weight=weight, capacity=capacity))

    def set_edge_active(self, u: str, v: str, active: bool) -> bool:
        """Close/reopen a road. Returns True if an edge was found & updated."""
        found = False
        for e in self._adj.get(u, []):
            if e.to == v:
                e.active = active
                found = True
        if not self.directed:
            for e in self._adj.get(v, []):
                if e.to == u:
                    e.active = active
                    found = True
        return found

    def neighbors(self, node_id: str, only_active: bool = True) -> Iterator[Edge]:
        for e in self._adj.get(node_id, []):
            if not only_active or e.active:
                yield e

    def nodes(self) -> Iterable[str]:
        return self._adj.keys()

    def edges(self, only_active: bool = True) -> Iterator[tuple[str, str, Edge]]:
        seen = set()
        for u, elist in self._adj.items():
            for e in elist:
                if only_active and not e.active:
                    continue
                key = (u, e.to) if self.directed else tuple(sorted((u, e.to)))
                if not self.directed and key in seen:
                    continue
                seen.add(key)
                yield u, e.to, e

    @property
    def num_nodes(self) -> int:
        return len(self._adj)

    @property
    def num_edges(self) -> int:
        return sum(1 for _ in self.edges())

    def copy(self) -> Graph:
        g = Graph(directed=self.directed)
        g._nodes = {k: dict(v) for k, v in self._nodes.items()}
        g._adj = {k: [Edge(e.to, e.weight, e.capacity, e.active, e.id) for e in v] for k, v in self._adj.items()}
        return g
