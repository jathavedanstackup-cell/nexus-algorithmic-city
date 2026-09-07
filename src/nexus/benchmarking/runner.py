"""Benchmark runner: records real measurements (never fabricated) for
routing algorithms across seeded city profiles, writing JSON results to
benchmarks/results/."""
from __future__ import annotations

import json
import platform
import tracemalloc
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from nexus.algorithms.routing import astar, dijkstra
from nexus.city.city import City

RESULTS_DIR = Path(__file__).resolve().parents[3] / "benchmarks" / "results"


@dataclass
class BenchmarkRecord:
    profile: str
    input_size: int
    algorithm: str
    seed: int
    runtime_ms: float
    nodes_explored: int
    edge_relaxations: int
    path_cost: float
    path_found: bool
    memory_kb: float
    timestamp: str
    machine: str


def run_benchmark(profile: str, seed: int = 42, algorithms=("dijkstra", "astar")) -> list[BenchmarkRecord]:
    city = City(profile=profile, seed=seed)
    nodes = list(city.graph.nodes())
    start, goal = nodes[0], nodes[-1]
    records: list[BenchmarkRecord] = []
    machine = f"{platform.system()} {platform.machine()} py{platform.python_version()}"

    fn_map = {"dijkstra": dijkstra, "astar": astar}
    for algo in algorithms:
        fn = fn_map[algo]
        tracemalloc.start()
        result = fn(city.graph, start, goal)
        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        records.append(BenchmarkRecord(
            profile=profile,
            input_size=city.graph.num_nodes,
            algorithm=algo,
            seed=seed,
            runtime_ms=round(result.runtime_ms, 4),
            nodes_explored=result.nodes_explored,
            edge_relaxations=result.edge_relaxations,
            path_cost=result.cost,
            path_found=result.found,
            memory_kb=round(peak / 1024, 2),
            timestamp=datetime.now(UTC).isoformat(),
            machine=machine,
        ))
    return records


def write_results(records: list[BenchmarkRecord], filename: str = "benchmark_results.jsonl") -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / filename
    with path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(asdict(r)) + "\n")
    return path
