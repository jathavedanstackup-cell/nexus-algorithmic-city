"""Runtime metrics aggregation exposed via GET /api/v1/metrics."""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class MetricsStore:
    started_at: float = field(default_factory=time.time)
    route_calls: int = 0
    dispatch_calls: int = 0
    evacuation_calls: int = 0
    benchmark_runs: int = 0
    last_route_runtimes: dict[str, float] = field(default_factory=dict)

    def record_route(self, algorithm: str, runtime_ms: float) -> None:
        self.route_calls += 1
        self.last_route_runtimes[algorithm] = runtime_ms

    def snapshot(self) -> dict:
        return {
            "uptime_seconds": round(time.time() - self.started_at, 2),
            "route_calls": self.route_calls,
            "dispatch_calls": self.dispatch_calls,
            "evacuation_calls": self.evacuation_calls,
            "benchmark_runs": self.benchmark_runs,
            "last_route_runtimes_ms": self.last_route_runtimes,
        }


metrics_store = MetricsStore()
