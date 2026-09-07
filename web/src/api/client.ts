// Thin REST client for the NEXUS API. No mocked data -- every call hits the
// real FastAPI backend (proxied to :8000 in dev, same-origin in prod).

export interface CitySnapshot {
  profile: string
  seed: number
  population: number
  num_nodes: number
  num_edges: number
  vehicles: number
  active_incidents: number
  stations: string[]
  hospitals: string[]
}

export interface SimulationSnapshot {
  simulation_id: string
  city: CitySnapshot
  timeline_length: number
}

export interface RouteResult {
  path: string[]
  cost: number
  nodes_explored: number
  edge_relaxations: number
  runtime_ms: number
  algorithm: string
  optimal_guaranteed: boolean
  found: boolean
}

export interface RouteCompare {
  requested_algorithm: string
  dijkstra: RouteResult
  astar: RouteResult
  agree_on_cost: boolean
}

export interface EvacuationReport {
  scenario: string
  max_flow: number
  bottleneck_edge: [string, string, number] | null
  critical_cut: [string, string][]
  at_risk_population: number
  reachable_from_source: string[]
}

export interface DispatchTelemetry {
  incident_id: string
  stage_log: string[]
  dispatched_unit: string | null
  route: RouteResult | null
  telemetry: Record<string, unknown>
  candidates: { unit_id: string; eta: number; rank_score: number }[]
}

export interface BenchmarkRecord {
  profile: string
  input_size: number
  algorithm: string
  seed: number
  runtime_ms: number
  nodes_explored: number
  edge_relaxations: number
  path_cost: number
  path_found: boolean
  memory_kb: number
  timestamp: string
  machine: string
}

export interface TimelineEvent {
  id: string
  timestamp: string
  kind: string
  description: string
  data: Record<string, unknown>
}

export interface ChaosReport {
  seed: number
  actions: string[]
  incidents_triggered: string[]
  dispatch_outcomes: { incident_id: string; dispatched_unit: string | null; candidates: number }[]
  components_after: number
  isolated_zones: string[]
  graceful_failures: string[]
  survived: boolean
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${body}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  health: () => req<{ status: string }>('/health'),
  createSimulation: (profile: string, seed: number) =>
    req<SimulationSnapshot>('/api/v1/simulations', { method: 'POST', body: JSON.stringify({ profile, seed }) }),
  getCity: (simId?: string) =>
    req<SimulationSnapshot>(`/api/v1/city${simId ? `?simulation_id=${simId}` : ''}`),
  getTimeline: (simId: string) =>
    req<{ timeline: TimelineEvent[] }>(`/api/v1/simulations/${simId}/timeline`),
  postEvent: (simId: string, kind: string, zone?: string) =>
    req(`/api/v1/simulations/${simId}/events`, { method: 'POST', body: JSON.stringify({ kind, zone }) }),
  getDispatch: (simId: string, incidentId: string, algorithm = 'astar') =>
    req<DispatchTelemetry>(`/api/v1/simulations/${simId}/dispatch/${incidentId}?algorithm=${algorithm}`),
  postRoute: (simId: string, start: string, goal: string) =>
    req<RouteCompare>('/api/v1/routes', {
      method: 'POST',
      body: JSON.stringify({ simulation_id: simId, start, goal }),
    }),
  postEvacuation: (scenario: string) =>
    req<EvacuationReport>('/api/v1/evacuation', { method: 'POST', body: JSON.stringify({ scenario }) }),
  postChaos: (simId: string, seed: number) =>
    req<ChaosReport>(`/api/v1/chaos?simulation_id=${simId}&seed=${seed}`, { method: 'POST' }),
  postBenchmark: (profile: string, seed: number) =>
    req<{ records: BenchmarkRecord[] }>('/api/v1/benchmarks', {
      method: 'POST',
      body: JSON.stringify({ profile, seed, algorithms: ['dijkstra', 'astar'] }),
    }),
  getMetrics: () => req<Record<string, unknown>>('/api/v1/metrics'),
}
