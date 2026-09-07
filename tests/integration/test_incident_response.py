import random

from nexus.city.city import City
from nexus.emergency.dispatch import recalculate, run_dispatch
from nexus.events import events as ev


def test_fire_incident_triggers_dispatch_end_to_end():
    city = City(profile="small", seed=1)
    rng = random.Random(1)
    result = ev.trigger_fire(city, "industrial_1", rng)
    assert result.incident_id in [i.id for i in city.incidents.values()]

    dispatch = run_dispatch(city, result.incident_id)
    assert len(dispatch.stage_log) == 5
    assert dispatch.dispatched_unit is not None
    dispatched_vehicle = city.vehicles.get(dispatch.dispatched_unit)
    assert dispatched_vehicle.status == "dispatched"
    assert dispatch.route is not None
    assert dispatch.route.found


def test_road_closure_forces_recalculation():
    city = City(profile="small", seed=2)
    rng = random.Random(2)
    result = ev.trigger_fire(city, "industrial_1", rng)
    dispatch = run_dispatch(city, result.incident_id)
    assert dispatch.dispatched_unit is not None

    # Close the first edge on the chosen route and force a recalculation.
    if len(dispatch.route.path) >= 2:
        u, v = dispatch.route.path[0], dispatch.route.path[1]
        city.graph.set_edge_active(u, v, False)
        new_route = recalculate(city, dispatch.dispatched_unit, result.incident_id)
        # Either an alternate route is found (possibly costlier) or none exists;
        # either way, recalculation must not silently reuse a closed edge.
        if new_route.found:
            for i in range(len(new_route.path) - 1):
                a, b = new_route.path[i], new_route.path[i + 1]
                assert not (a == u and b == v)


def test_flood_disaster_mutates_state():
    city = City(profile="small", seed=3)
    rng = random.Random(3)
    before_edges = city.graph.num_edges
    result = ev.trigger_flood(city, "north_district", rng)
    after_edges = city.graph.num_edges
    assert after_edges <= before_edges  # some roads may have closed
    assert result.incident_id in [i.id for i in city.incidents.values()]


def test_power_failure_marks_nodes_down():
    city = City(profile="small", seed=4)
    result = ev.trigger_power_failure(city, "district_7")
    affected = [n for n in result.affected_nodes]
    assert all(city.graph.node_attrs(n).get("power") == "down" for n in affected)


def test_no_units_available_dispatch_reports_none_gracefully():
    city = City(profile="small", seed=5)
    for v in city.vehicles.values():
        v.status = "dispatched"
    rng = random.Random(5)
    result = ev.trigger_fire(city, "industrial_1", rng)
    dispatch = run_dispatch(city, result.incident_id)
    assert dispatch.dispatched_unit is None
    assert "no available unit" in dispatch.stage_log[-2].lower() or "no available unit" in " ".join(dispatch.stage_log).lower()
