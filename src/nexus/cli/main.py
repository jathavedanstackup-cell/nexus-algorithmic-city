"""NEXUS CLI: full product usable without the web UI.

    python -m nexus.cli demo
    python -m nexus.cli simulate --profile medium --seed 42
    python -m nexus.cli disaster --type fire --zone industrial_1
    python -m nexus.cli evacuate --scenario bridge_closure
    python -m nexus.cli route --from station_1 --to hospital_1 --algorithm astar
    python -m nexus.cli benchmark --profile large
    python -m nexus.cli chaos --seed 42
"""
from __future__ import annotations

import json
import random
import sys

import click

from nexus.algorithms.routing import astar, dijkstra
from nexus.benchmarking.runner import run_benchmark, write_results
from nexus.chaos.chaos import run_chaos
from nexus.city.city import PROFILES, City
from nexus.emergency.dispatch import run_dispatch
from nexus.evacuation.evacuation import run_evacuation
from nexus.events import events as ev


def _echo_json(data) -> None:
    click.echo(json.dumps(data, indent=2, default=str))


@click.group()
def cli() -> None:
    """NEXUS: a living city powered by data structures & algorithms."""


@cli.command()
def demo() -> None:
    """Run a short end-to-end demo: build a city, trigger a fire, dispatch,
    then run an evacuation analysis -- good first command for reviewers."""
    try:
        city = City(profile="small", seed=42)
        click.echo(f"City built: {city.snapshot()}")
        rng = random.Random(42)
        result = ev.trigger_fire(city, "industrial_1", rng)
        click.echo(f"Event: {result.description}")
        dispatch = run_dispatch(city, result.incident_id)
        click.echo("Dispatch pipeline:")
        for line in dispatch.stage_log:
            click.echo(f"  {line}")
        click.echo(f"Dispatched unit: {dispatch.dispatched_unit}")
        report = run_evacuation(None, "bridge_closure")
        click.echo(f"Evacuation max flow: {report.max_flow} (bottleneck: {report.bottleneck_edge})")
    except Exception as exc:  # noqa: BLE001
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--profile", default="small", type=click.Choice(list(PROFILES)))
@click.option("--seed", default=42, type=int)
def simulate(profile: str, seed: int) -> None:
    """Build and print a city simulation snapshot for the given profile/seed."""
    try:
        city = City(profile=profile, seed=seed)
        _echo_json(city.snapshot())
    except Exception as exc:  # noqa: BLE001
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--type", "kind", required=True, type=click.Choice(["fire", "flood", "power_failure"]))
@click.option("--zone", default="industrial_1")
@click.option("--profile", default="small", type=click.Choice(list(PROFILES)))
@click.option("--seed", default=42, type=int)
def disaster(kind: str, zone: str, profile: str, seed: int) -> None:
    """Trigger a disaster event against a fresh seeded city and show effects."""
    try:
        city = City(profile=profile, seed=seed)
        rng = random.Random(seed)
        if kind == "fire":
            res = ev.trigger_fire(city, zone, rng)
        elif kind == "flood":
            res = ev.trigger_flood(city, zone, rng)
        else:
            res = ev.trigger_power_failure(city, zone)
        _echo_json(res.__dict__)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--scenario", default="bridge_closure")
def evacuate(scenario: str) -> None:
    """Run max-flow evacuation analysis for a scenario (demo graph by default)."""
    try:
        report = run_evacuation(None, scenario)
        _echo_json({
            "scenario": report.scenario,
            "max_flow": report.max_flow,
            "bottleneck_edge": report.bottleneck_edge,
            "critical_cut": report.critical_cut,
            "at_risk_population": report.at_risk_population,
        })
    except Exception as exc:  # noqa: BLE001
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)


@cli.command(name="route")
@click.option("--from", "start", required=True)
@click.option("--to", "goal", required=True)
@click.option("--algorithm", default="astar", type=click.Choice(["astar", "dijkstra"]))
@click.option("--profile", default="small", type=click.Choice(list(PROFILES)))
@click.option("--seed", default=42, type=int)
def route_cmd(start: str, goal: str, algorithm: str, profile: str, seed: int) -> None:
    """Compute a route between two node ids in a fresh seeded city."""
    try:
        city = City(profile=profile, seed=seed)
        if not city.graph.has_node(start) or not city.graph.has_node(goal):
            sample = list(city.graph.nodes())[:5]
            raise click.ClickException(
                f"'{start}' or '{goal}' not found in this city. Example valid nodes: {sample}"
            )
        fn = astar if algorithm == "astar" else dijkstra
        result = fn(city.graph, start, goal)
        _echo_json(result.__dict__)
    except click.ClickException:
        raise
    except Exception as exc:  # noqa: BLE001
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--profile", default="small", type=click.Choice(list(PROFILES)))
@click.option("--seed", default=42, type=int)
def benchmark(profile: str, seed: int) -> None:
    """Run and persist a real benchmark for the given profile."""
    try:
        records = run_benchmark(profile, seed=seed)
        path = write_results(records)
        click.echo(f"Wrote {len(records)} records to {path}")
        _echo_json([r.__dict__ for r in records])
    except Exception as exc:  # noqa: BLE001
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--seed", default=42, type=int)
@click.option("--profile", default="small", type=click.Choice(list(PROFILES)))
@click.option("--intensity", default=4, type=int)
def chaos(seed: int, profile: str, intensity: int) -> None:
    """Run chaos mode: composed failures, deterministic per seed, never crashes."""
    try:
        city = City(profile=profile, seed=seed)
        report = run_chaos(city, seed=seed, intensity=intensity)
        _echo_json(report.__dict__)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
