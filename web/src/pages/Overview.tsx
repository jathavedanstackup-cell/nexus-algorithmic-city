import { useEffect, useState } from 'react'
import { MetricCard } from '../components/MetricCard'
import { NetworkCanvas } from '../components/NetworkCanvas'
import { StatusBadge } from '../components/StatusBadge'
import { ControlBar } from '../components/ControlBar'
import { useSimulation } from '../SimulationContext'
import { api } from '../api/client'
import type { BenchmarkRecord } from '../api/client'

export function Overview() {
  const { city, profile, seed, setProfile, setSeed, rebuild, loading, error } = useSimulation()
  const [clock, setClock] = useState(new Date())
  const [bench, setBench] = useState<BenchmarkRecord[] | null>(null)
  const [benchError, setBenchError] = useState<string | null>(null)

  useEffect(() => {
    const id = setInterval(() => setClock(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    api.postBenchmark('small', seed)
      .then((r) => setBench(r.records))
      .catch((e) => setBenchError(e instanceof Error ? e.message : String(e)))
  }, [seed])

  const dijkstra = bench?.find((b) => b.algorithm === 'dijkstra')
  const astar = bench?.find((b) => b.algorithm === 'astar')

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>NEXUS Command Center</h1>
          <p>A living city powered by data structures &amp; algorithms.</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="live-pill"><span className="live-dot" /> LIVE</div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--text-dim)' }}>
            {clock.toLocaleTimeString()}
          </div>
        </div>
      </div>

      <ControlBar profile={profile} seed={seed} onProfileChange={setProfile} onSeedChange={setSeed} onRebuild={rebuild} busy={loading} />

      <div className="grid grid-4" style={{ marginBottom: 24 }}>
        <MetricCard label="Population" value={city?.population.toLocaleString()} loading={loading} error={error} sub={city ? `profile: ${city.profile}` : undefined} />
        <MetricCard label="Vehicles" value={city?.vehicles} loading={loading} error={error} sub="fire / ambulance / police" />
        <MetricCard label="Active Incidents" value={city?.active_incidents} loading={loading} error={error} />
        <MetricCard label="Network Size" value={city ? `${city.num_nodes}n / ${city.num_edges}e` : undefined} loading={loading} error={error} sub={`seed ${seed}`} />
      </div>

      <div className="grid grid-2">
        <div className="panel elevated">
          <h2 className="section-title">City Network</h2>
          <NetworkCanvas nodeCount={city?.num_nodes ?? 0} loading={loading} />
        </div>
        <div className="panel">
          <h2 className="section-title">Live Benchmark Readouts (small profile)</h2>
          {benchError && <div className="error-state">{benchError}</div>}
          {!bench && !benchError && <div className="loading-state">Running benchmark…</div>}
          {bench && (
            <div>
              <div className="arena-stat"><span>Dijkstra</span><span>{dijkstra?.runtime_ms.toFixed(2)} ms · {dijkstra?.nodes_explored} nodes</span></div>
              <div className="arena-stat"><span>A*</span><span>{astar?.runtime_ms.toFixed(2)} ms · {astar?.nodes_explored} nodes</span></div>
              <p style={{ color: 'var(--text-dim)', fontSize: 12, marginTop: 12 }}>
                A* explores fewer nodes than Dijkstra on the same seeded input while both
                converge on the same optimal path cost. Full comparisons in the Arena.
              </p>
            </div>
          )}
          <div style={{ marginTop: 16 }}>
            <StatusBadge tone="signal">Small</StatusBadge>{' '}
            <StatusBadge tone="signal">Medium</StatusBadge>{' '}
            <StatusBadge tone="warning">Large</StatusBadge>{' '}
            <StatusBadge tone="critical">Stress</StatusBadge>
          </div>
        </div>
      </div>
    </div>
  )
}
