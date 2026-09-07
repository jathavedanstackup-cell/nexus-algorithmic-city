"""Optimization domain: Greedy resource allocation, small DP (0/1 knapsack
style constrained optimization), and small Backtracking constraint solver.

These back the "Optimize" step of resource dispatch: given limited units
(fire trucks, ambulances) and incidents with severity/value, decide which
incidents to service under a capacity constraint.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Incident:
    id: str
    severity: float  # "value"
    cost: int  # units required


def greedy_allocate(incidents: list[Incident], available_units: int) -> tuple[list[str], int]:
    """Greedy by severity/cost ratio (classic fractional-greedy heuristic
    applied to the 0/1 case) — fast O(n log n), not always optimal."""
    ranked = sorted(incidents, key=lambda i: i.severity / max(i.cost, 1), reverse=True)
    chosen: list[str] = []
    remaining = available_units
    for inc in ranked:
        if inc.cost <= remaining:
            chosen.append(inc.id)
            remaining -= inc.cost
    return chosen, available_units - remaining


def dp_allocate(incidents: list[Incident], available_units: int) -> tuple[list[str], float]:
    """0/1 knapsack DP: exact optimum for small n / small capacity, used to
    validate/upgrade the greedy heuristic on Small/Medium profiles."""
    n = len(incidents)
    W = available_units
    dp = [[0.0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        inc = incidents[i - 1]
        for w in range(W + 1):
            dp[i][w] = dp[i - 1][w]
            if inc.cost <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - inc.cost] + inc.severity)
    # backtrack
    chosen: list[str] = []
    w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(incidents[i - 1].id)
            w -= incidents[i - 1].cost
    chosen.reverse()
    return chosen, dp[n][W]


def backtracking_zone_coloring(adjacency: dict, num_colors: int) -> dict | None:
    """Small constraint-satisfaction example: assign each zone a color
    (e.g. dispatch shift/resource pool) so no two adjacent zones share one.
    Returns an assignment dict, or None if infeasible with `num_colors`."""
    zones = list(adjacency.keys())
    assignment: dict = {}

    def is_valid(zone: str, color: int) -> bool:
        return all(assignment.get(nb) != color for nb in adjacency[zone])

    def backtrack(idx: int) -> bool:
        if idx == len(zones):
            return True
        zone = zones[idx]
        for color in range(num_colors):
            if is_valid(zone, color):
                assignment[zone] = color
                if backtrack(idx + 1):
                    return True
                del assignment[zone]
        return False

    return dict(assignment) if backtrack(0) else None
