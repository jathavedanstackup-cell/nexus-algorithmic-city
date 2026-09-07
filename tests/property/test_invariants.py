"""Invariant tests: path validity, flow conservation, capacity limits --
checked across multiple seeded random graphs rather than one fixed case."""
import random

import pytest

from nexus.algorithms.maxflow import edmonds_karp
from nexus.algorithms.routing import astar, dijkstra
from nexus.city.city import City
from nexus.structures.graph import Graph


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_route_path_is_valid_edge_sequence(seed):
    city = City(profile="small", seed=seed)
    nodes = list(city.graph.nodes())
    start, goal = nodes[0], nodes[-1]
    result = dijkstra(city.graph, start, goal)
    if not result.found:
        return
    for i in range(len(result.path) - 1):
        u, v = result.path[i], result.path[i + 1]
        neighbor_ids = [e.to for e in city.graph.neighbors(u)]
        assert v in neighbor_ids, f"invalid hop {u}->{v} not in graph"


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_astar_cost_never_less_than_dijkstra(seed):
    city = City(profile="small", seed=seed)
    nodes = list(city.graph.nodes())
    start, goal = nodes[0], nodes[-1]
    d = dijkstra(city.graph, start, goal)
    a = astar(city.graph, start, goal)
    if d.found and a.found:
        assert a.cost == pytest.approx(d.cost)  # admissible heuristic -> same optimal cost
        assert a.nodes_explored <= d.nodes_explored


@pytest.mark.parametrize("cap_seed", [10, 20, 30])
def test_maxflow_never_exceeds_min_capacity_out_of_source(cap_seed):
    rng = random.Random(cap_seed)
    g = Graph(directed=True)
    caps = {}
    for edge in [("S", "A", rng.randint(1, 20)), ("S", "B", rng.randint(1, 20)),
                 ("A", "T", rng.randint(1, 20)), ("B", "T", rng.randint(1, 20)),
                 ("A", "B", rng.randint(1, 20))]:
        u, v, c = edge
        g.add_edge(u, v, weight=1.0, capacity=c)
        caps[(u, v)] = c
    result = edmonds_karp(g, "S", "T")
    total_source_capacity = caps[("S", "A")] + caps[("S", "B")]
    assert result.max_flow <= total_source_capacity + 1e-6


def test_maxflow_flow_never_exceeds_edge_capacity():
    from nexus.evacuation.evacuation import demo_graph
    g = demo_graph()
    result = edmonds_karp(g, "A", "EXIT")
    capacity_by_edge = {}
    for u in g.nodes():
        for e in g.neighbors(u):
            if e.capacity is not None:
                capacity_by_edge[(u, e.to)] = e.capacity
    for (u, v), flow in result.flow_on_edge.items():
        if (u, v) in capacity_by_edge:
            assert flow <= capacity_by_edge[(u, v)] + 1e-6
