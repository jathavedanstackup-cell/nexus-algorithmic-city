"""Edmonds-Karp (BFS-augmenting-path) max-flow, used for evacuation capacity
analysis: max flow value, saturated bottleneck edge(s), and the min-cut
(critical cut) via residual-graph reachability from the source."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from nexus.structures.graph import Graph

INF = float("inf")


@dataclass
class MaxFlowResult:
    max_flow: float
    flow_on_edge: dict[tuple[str, str], float]
    bottleneck_edges: list[tuple[str, str, float]]
    critical_cut: list[tuple[str, str]]
    reachable_from_source: list[str]
    at_risk_nodes: list[str]


def edmonds_karp(graph: Graph, source: str, sink: str) -> MaxFlowResult:
    # Build a residual capacity map from the (directed) graph's edges.
    capacity: dict[tuple[str, str], float] = {}
    for u in graph.nodes():
        for e in graph.neighbors(u):
            if e.capacity is None:
                continue
            capacity[(u, e.to)] = capacity.get((u, e.to), 0.0) + e.capacity
            capacity.setdefault((e.to, u), 0.0)

    flow: dict[tuple[str, str], float] = {k: 0.0 for k in capacity}

    def residual(u: str, v: str) -> float:
        return capacity.get((u, v), 0.0) - flow.get((u, v), 0.0)

    def bfs_augment() -> tuple[list[str], float]:
        parent: dict[str, str] = {source: source}
        q = deque([source])
        while q:
            u = q.popleft()
            if u == sink:
                break
            for (a, b) in capacity:
                if a != u or b in parent:
                    continue
                if residual(a, b) > 1e-9:
                    parent[b] = a
                    q.append(b)
        if sink not in parent:
            return [], 0.0
        path = [sink]
        while path[-1] != source:
            path.append(parent[path[-1]])
        path.reverse()
        bottleneck = min(residual(path[i], path[i + 1]) for i in range(len(path) - 1))
        return path, bottleneck

    max_flow = 0.0
    while True:
        path, bottleneck = bfs_augment()
        if not path or bottleneck <= 0:
            break
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            flow[(a, b)] = flow.get((a, b), 0.0) + bottleneck
            flow[(b, a)] = flow.get((b, a), 0.0) - bottleneck
        max_flow += bottleneck

    # Min-cut: nodes reachable from source in the *final* residual graph.
    reachable = {source}
    q = deque([source])
    while q:
        u = q.popleft()
        for (a, b), cap in capacity.items():
            if a == u and b not in reachable and residual(a, b) > 1e-9:
                reachable.add(b)
                q.append(b)

    critical_cut: list[tuple[str, str]] = []
    bottleneck_edges: list[tuple[str, str, float]] = []
    for (a, b), cap in capacity.items():
        if a in reachable and b not in reachable and cap > 0:
            critical_cut.append((a, b))
            used = flow.get((a, b), 0.0)
            if used >= cap - 1e-6 and cap > 0:
                bottleneck_edges.append((a, b, cap))

    at_risk = [n for n in graph.nodes() if n not in reachable and n != sink]

    return MaxFlowResult(
        max_flow=max_flow,
        flow_on_edge={k: v for k, v in flow.items() if v > 1e-9},
        bottleneck_edges=sorted(bottleneck_edges, key=lambda x: x[2]),
        critical_cut=critical_cut,
        reachable_from_source=sorted(reachable),
        at_risk_nodes=sorted(at_risk),
    )
