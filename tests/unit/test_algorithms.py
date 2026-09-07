import pytest

from nexus.algorithms.maxflow import edmonds_karp
from nexus.algorithms.routing import astar, dijkstra
from nexus.algorithms.traversal import bfs, dfs_components
from nexus.evacuation.evacuation import demo_graph
from nexus.structures.graph import Graph


def _line_graph():
    g = Graph()
    g.add_edge("a", "b", weight=1)
    g.add_edge("b", "c", weight=1)
    g.add_edge("c", "d", weight=1)
    return g


def test_bfs_reachability():
    g = _line_graph()
    result = bfs(g, "a")
    assert result.visited == {"a", "b", "c", "d"}
    assert result.order[0] == "a"


def test_bfs_empty_graph():
    g = Graph()
    result = bfs(g, "missing")
    assert result.visited == set()
    assert result.nodes_explored == 0


def test_dfs_components_disconnected():
    g = Graph()
    g.add_edge("a", "b")
    g.add_node("isolated")
    comps = dfs_components(g)
    sizes = sorted(len(c) for c in comps)
    assert sizes == [1, 2]


def test_dijkstra_finds_shortest_path():
    g = Graph()
    g.add_edge("a", "b", weight=1)
    g.add_edge("b", "c", weight=1)
    g.add_edge("a", "c", weight=5)
    result = dijkstra(g, "a", "c")
    assert result.found
    assert result.path == ["a", "b", "c"]
    assert result.cost == 2


def test_dijkstra_disconnected_returns_not_found():
    g = Graph()
    g.add_node("a")
    g.add_node("b")
    result = dijkstra(g, "a", "b")
    assert not result.found
    assert result.cost == float("inf")


def test_dijkstra_missing_nodes():
    g = Graph()
    result = dijkstra(g, "x", "y")
    assert not result.found


def test_astar_dijkstra_agree_on_cost():
    g = Graph()
    for i in range(20):
        g.add_node(f"n{i}", x=i, y=0)
    for i in range(19):
        g.add_edge(f"n{i}", f"n{i+1}", weight=1.0)
    # add a shortcut so there's more than one path
    g.add_edge("n0", "n10", weight=3.0)
    d = dijkstra(g, "n0", "n19")
    a = astar(g, "n0", "n19")
    assert d.found and a.found
    assert d.cost == pytest.approx(a.cost)
    # A* with an admissible heuristic should explore no more nodes than Dijkstra
    assert a.nodes_explored <= d.nodes_explored


def test_astar_duplicate_and_empty_graph():
    g = Graph()
    result = astar(g, "a", "b")
    assert not result.found


def test_maxflow_known_graph():
    g = demo_graph()
    result = edmonds_karp(g, "A", "EXIT")
    assert result.max_flow == 15
    assert ("A", "B") in result.critical_cut or ("A", "C") in result.critical_cut


def test_maxflow_bridge_closure_reduces_flow():
    g = demo_graph()
    g.set_edge_active("B", "D", False)
    result = edmonds_karp(g, "A", "EXIT")
    assert result.max_flow < 15


def test_maxflow_no_path():
    g = Graph(directed=True)
    g.add_node("A")
    g.add_node("B")
    result = edmonds_karp(g, "A", "B")
    assert result.max_flow == 0


def test_maxflow_flow_conservation():
    g = demo_graph()
    result = edmonds_karp(g, "A", "EXIT")
    inflow = {}
    outflow = {}
    for (u, v), f in result.flow_on_edge.items():
        outflow[u] = outflow.get(u, 0) + f
        inflow[v] = inflow.get(v, 0) + f
    for node in ("B", "C", "D"):
        assert inflow.get(node, 0) == pytest.approx(outflow.get(node, 0))
