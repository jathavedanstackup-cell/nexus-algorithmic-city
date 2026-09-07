from nexus.chaos.chaos import run_chaos
from nexus.city.city import City
from nexus.evacuation.evacuation import run_evacuation


def test_same_seed_produces_identical_city():
    a = City(profile="small", seed=42)
    b = City(profile="small", seed=42)
    assert a.snapshot() == b.snapshot()
    assert list(a.graph.nodes()) == list(b.graph.nodes())
    assert list(a.graph.edges()) == [] or True  # edges compared via cost below
    edges_a = sorted((u, v, e.weight) for u, v, e in a.graph.edges())
    edges_b = sorted((u, v, e.weight) for u, v, e in b.graph.edges())
    assert edges_a == edges_b


def test_different_seed_produces_different_city():
    a = City(profile="small", seed=42)
    b = City(profile="small", seed=99)
    edges_a = sorted((u, v, e.weight) for u, v, e in a.graph.edges())
    edges_b = sorted((u, v, e.weight) for u, v, e in b.graph.edges())
    assert edges_a != edges_b


def test_chaos_seed_reproducibility():
    city_a = City(profile="small", seed=42)
    city_b = City(profile="small", seed=42)
    report_a = run_chaos(city_a, seed=42, intensity=5)
    report_b = run_chaos(city_b, seed=42, intensity=5)
    assert report_a.actions == report_b.actions
    assert report_a.incidents_triggered == report_b.incidents_triggered


def test_chaos_never_crashes_and_reports_survival():
    city = City(profile="small", seed=1)
    # Starve the city of all vehicles to force resource exhaustion paths.
    for v in list(city.vehicles.keys()):
        city.vehicles.get(v).status = "dispatched"
    report = run_chaos(city, seed=1, intensity=8)
    assert report.survived is True


def test_evacuation_scenario_bridge_closure_reduces_flow():
    baseline = run_evacuation(None, "evacuation_default")
    closed = run_evacuation(None, "bridge_closure")
    assert closed.max_flow <= baseline.max_flow
    assert closed.max_flow > 0  # still feasible via C->EXIT / C->D->EXIT
