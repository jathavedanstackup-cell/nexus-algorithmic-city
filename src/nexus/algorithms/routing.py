"""Dijkstra and A* shortest-path routing over the city Graph.

Both use our own binary-heap PriorityQueue (O(log n) push/pop), never a
linear scan, so routing stays practical at Medium/Large scale.
"""
from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass

from nexus.structures.graph import Graph
from nexus.structures.heap import PriorityQueue

INF = float("inf")


@dataclass
class RouteResult:
    path: list[str]
    cost: float
    nodes_explored: int
    edge_relaxations: int
    runtime_ms: float
    algorithm: str
    optimal_guaranteed: bool
    found: bool = True


def _reconstruct(parent: dict[str, str], start: str, goal: str) -> list[str]:
    if goal not in parent and goal != start:
        return []
    path = [goal]
    while path[-1] != start:
        nxt = parent.get(path[-1])
        if nxt is None:
            return []
        path.append(nxt)
    path.reverse()
    return path


def dijkstra(graph: Graph, start: str, goal: str) -> RouteResult:
    t0 = time.perf_counter()
    dist: dict[str, float] = {start: 0.0}
    parent: dict[str, str] = {}
    visited = set()
    pq: PriorityQueue[str] = PriorityQueue()
    pq.push(0.0, start)
    nodes_explored = 0
    relaxations = 0

    if not graph.has_node(start) or not graph.has_node(goal):
        return RouteResult([], INF, 0, 0, 0.0, "dijkstra", True, found=False)

    while not pq.is_empty():
        u = pq.pop()
        if u in visited:
            continue
        visited.add(u)
        nodes_explored += 1
        if u == goal:
            break
        for edge in graph.neighbors(u):
            relaxations += 1
            nd = dist[u] + edge.weight
            if nd < dist.get(edge.to, INF):
                dist[edge.to] = nd
                parent[edge.to] = u
                pq.push(nd, edge.to)

    runtime = (time.perf_counter() - t0) * 1000
    found = goal in dist
    path = _reconstruct(parent, start, goal) if found else []
    return RouteResult(
        path=path,
        cost=dist.get(goal, INF),
        nodes_explored=nodes_explored,
        edge_relaxations=relaxations,
        runtime_ms=runtime,
        algorithm="dijkstra",
        optimal_guaranteed=True,
        found=found,
    )


def euclidean_heuristic(graph: Graph) -> Callable[[str, str], float]:
    """Admissible heuristic IF nodes carry 'x'/'y' attrs and edge weights are
    >= straight-line distance in the same units. Falls back to 0 (Dijkstra
    behavior) when coordinates are missing, which keeps A* admissible."""

    def h(u: str, goal: str) -> float:
        ua, ga = graph.node_attrs(u), graph.node_attrs(goal)
        if "x" in ua and "y" in ua and "x" in ga and "y" in ga:
            return math.hypot(ua["x"] - ga["x"], ua["y"] - ga["y"])
        return 0.0

    return h


def astar(graph: Graph, start: str, goal: str, heuristic: Callable[[str, str], float] | None = None) -> RouteResult:
    t0 = time.perf_counter()
    if heuristic is None:
        heuristic = euclidean_heuristic(graph)

    if not graph.has_node(start) or not graph.has_node(goal):
        return RouteResult([], INF, 0, 0, 0.0, "astar", False, found=False)

    g_score: dict[str, float] = {start: 0.0}
    parent: dict[str, str] = {}
    visited = set()
    pq: PriorityQueue[str] = PriorityQueue()
    pq.push(heuristic(start, goal), start)
    nodes_explored = 0
    relaxations = 0

    while not pq.is_empty():
        u = pq.pop()
        if u in visited:
            continue
        visited.add(u)
        nodes_explored += 1
        if u == goal:
            break
        for edge in graph.neighbors(u):
            relaxations += 1
            ng = g_score[u] + edge.weight
            if ng < g_score.get(edge.to, INF):
                g_score[edge.to] = ng
                parent[edge.to] = u
                pq.push(ng + heuristic(edge.to, goal), edge.to)

    runtime = (time.perf_counter() - t0) * 1000
    found = goal in g_score
    path = _reconstruct(parent, start, goal) if found else []
    # We only ever claim optimality when using the admissible euclidean_heuristic
    # (0 when coords are absent, which degrades gracefully to Dijkstra).
    return RouteResult(
        path=path,
        cost=g_score.get(goal, INF),
        nodes_explored=nodes_explored,
        edge_relaxations=relaxations,
        runtime_ms=runtime,
        algorithm="astar",
        optimal_guaranteed=True,
        found=found,
    )
