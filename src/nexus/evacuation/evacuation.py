"""Evacuation Command: max-flow analysis over the city graph (or a supplied
small demo graph) reporting max flow, bottleneck edge(s), critical cut, and
an at-risk population estimate for nodes cut off from the exit."""
from __future__ import annotations

from dataclasses import dataclass

from nexus.algorithms.maxflow import MaxFlowResult, edmonds_karp
from nexus.city.city import City
from nexus.structures.graph import Graph


def demo_graph() -> Graph:
    """The canonical known test graph: A/B/C/D/EXIT with capacities, used to
    verify max-flow correctness (documented expected max flow = 15)."""
    g = Graph(directed=True)
    edges = [
        ("A", "B", 10), ("A", "C", 5),
        ("B", "C", 4), ("B", "D", 8),
        ("C", "EXIT", 10), ("D", "EXIT", 10),
        ("C", "D", 6),
    ]
    for u, v, cap in edges:
        g.add_edge(u, v, weight=1.0, capacity=cap)
    return g


@dataclass
class EvacuationReport:
    scenario: str
    max_flow: float
    bottleneck_edge: tuple[str, str, float] | None
    critical_cut: list[tuple[str, str]]
    at_risk_population: int
    result: MaxFlowResult


def run_evacuation(city: City | None, scenario: str, source: str = "A", sink: str = "EXIT") -> EvacuationReport:
    if scenario == "bridge_closure" or city is None:
        graph = demo_graph()
        if scenario == "bridge_closure":
            graph.set_edge_active("B", "D", False)
        result = edmonds_karp(graph, source, sink)
        at_risk_pop = len(result.at_risk_nodes) * 500
    else:
        # Use the live city graph: pick a source zone and the nearest hospital
        # as the evacuation sink, with node capacities implied by edge caps.
        nodes = list(city.graph.nodes())
        src = source if city.graph.has_node(source) else nodes[0]
        snk = sink if city.graph.has_node(sink) else (city.hospitals[0] if city.hospitals else nodes[-1])
        directed = Graph(directed=True)
        for u, v, e in city.graph.edges():
            directed.add_edge(u, v, weight=e.weight, capacity=e.capacity or 1)
            directed.add_edge(v, u, weight=e.weight, capacity=e.capacity or 1)
        result = edmonds_karp(directed, src, snk)
        at_risk_pop = len(result.at_risk_nodes) * (city.population // max(city.graph.num_nodes, 1))

    bottleneck = result.bottleneck_edges[0] if result.bottleneck_edges else None
    return EvacuationReport(
        scenario=scenario,
        max_flow=result.max_flow,
        bottleneck_edge=bottleneck,
        critical_cut=result.critical_cut,
        at_risk_population=at_risk_pop,
        result=result,
    )
