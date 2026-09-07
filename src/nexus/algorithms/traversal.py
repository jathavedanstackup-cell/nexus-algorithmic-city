"""BFS (reachability / shortest hop-count) and DFS (connected components)."""
from __future__ import annotations

from dataclasses import dataclass, field

from nexus.structures.graph import Graph
from nexus.structures.queue import Queue


@dataclass
class TraversalResult:
    order: list[str]
    visited: set[str]
    nodes_explored: int
    parent: dict[str, str] = field(default_factory=dict)


def bfs(graph: Graph, start: str) -> TraversalResult:
    """Breadth-first search: used for reachability and hop-count distance."""
    if not graph.has_node(start):
        return TraversalResult(order=[], visited=set(), nodes_explored=0)
    visited: set[str] = {start}
    order: list[str] = []
    parent: dict[str, str] = {}
    q: Queue[str] = Queue()
    q.enqueue(start)
    explored = 0
    while not q.is_empty():
        u = q.dequeue()
        order.append(u)
        explored += 1
        for edge in graph.neighbors(u):
            if edge.to not in visited:
                visited.add(edge.to)
                parent[edge.to] = u
                q.enqueue(edge.to)
    return TraversalResult(order=order, visited=visited, nodes_explored=explored, parent=parent)


def dfs_components(graph: Graph) -> list[set[str]]:
    """Depth-first search used to enumerate connected components."""
    seen: set[str] = set()
    components: list[set[str]] = []
    for node in graph.nodes():
        if node in seen:
            continue
        stack = [node]
        comp: set[str] = set()
        while stack:
            u = stack.pop()
            if u in comp:
                continue
            comp.add(u)
            for edge in graph.neighbors(u):
                if edge.to not in comp:
                    stack.append(edge.to)
        seen |= comp
        components.append(comp)
    return components
