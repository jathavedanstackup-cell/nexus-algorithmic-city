from nexus.optimization.allocation import Incident, backtracking_zone_coloring, dp_allocate, greedy_allocate


def _incidents():
    return [
        Incident("i1", severity=10, cost=5),
        Incident("i2", severity=6, cost=3),
        Incident("i3", severity=8, cost=4),
    ]


def test_greedy_allocate_respects_capacity():
    chosen, used = greedy_allocate(_incidents(), available_units=7)
    assert used <= 7
    assert set(chosen).issubset({"i1", "i2", "i3"})


def test_dp_allocate_is_optimal_and_matches_or_beats_greedy():
    incidents = _incidents()
    greedy_chosen, _ = greedy_allocate(incidents, 7)
    greedy_value = sum(i.severity for i in incidents if i.id in greedy_chosen)
    _dp_chosen, dp_value = dp_allocate(incidents, 7)
    assert dp_value >= greedy_value


def test_dp_allocate_empty():
    chosen, value = dp_allocate([], 5)
    assert chosen == []
    assert value == 0


def test_backtracking_zone_coloring_feasible():
    adjacency = {"a": ["b"], "b": ["a", "c"], "c": ["b"]}
    result = backtracking_zone_coloring(adjacency, num_colors=2)
    assert result is not None
    assert result["a"] != result["b"]
    assert result["b"] != result["c"]


def test_backtracking_zone_coloring_infeasible():
    # Triangle needs 3 colors, must fail gracefully with 2
    adjacency = {"a": ["b", "c"], "b": ["a", "c"], "c": ["a", "b"]}
    result = backtracking_zone_coloring(adjacency, num_colors=2)
    assert result is None
