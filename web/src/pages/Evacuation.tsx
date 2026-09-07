import { useEffect, useState } from 'react'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../api/client'
import type { EvacuationReport } from '../api/client'

const NODES = ['A', 'B', 'C', 'D', 'EXIT']
const EDGES: [string, string, number][] = [
  ['A', 'B', 10], ['A', 'C', 5], ['B', 'C', 4], ['B', 'D', 8], ['C', 'D', 6], ['C', 'EXIT', 10], ['D', 'EXIT', 10],
]

export function Evacuation() {
  const [scenario, setScenario] = useState('evacuation_default')
  const [report, setReport] = useState<EvacuationReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function run(s: string) {
    setScenario(s)
    setLoading(true)
    setError(null)
    try {
      const res = await api.postEvacuation(s)
      setReport(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { run('evacuation_default') }, [])

  const closedEdge = scenario === 'bridge_closure' ? 'B-D' : null

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Evacuation Command</h1>
          <p>Max-flow analysis (Edmonds-Karp) over a known A/B/C/D/EXIT network with capacities.</p>
        </div>
      </div>

      <div className="controls-row">
        <button className="btn" onClick={() => run('evacuation_default')} disabled={loading}>Baseline Network</button>
        <button className="btn danger" onClick={() => run('bridge_closure')} disabled={loading}>Simulate Bridge Closure (B-D)</button>
      </div>

      <div className="grid grid-2">
        <div className="panel elevated">
          <h2 className="section-title">Network</h2>
          <svg viewBox="0 0 300 220" style={{ width: '100%', height: 260 }}>
            {(() => {
              const pos: Record<string, [number, number]> = { A: [30, 110], B: [130, 40], C: [130, 180], D: [220, 110], EXIT: [280, 110] }
              return (
                <>
                  {EDGES.map(([u, v, cap], i) => {
                    const [x1, y1] = pos[u]
                    const [x2, y2] = pos[v]
                    const isClosed = closedEdge === `${u}-${v}` || closedEdge === `${v}-${u}`
                    const isBottleneck = report?.bottleneck_edge && report.bottleneck_edge[0] === u && report.bottleneck_edge[1] === v
                    return (
                      <g key={i}>
                        <line x1={x1} y1={y1} x2={x2} y2={y2}
                          stroke={isClosed ? '#ff5c72' : isBottleneck ? '#ffb454' : '#3fd0ff'}
                          strokeWidth={isBottleneck ? 3 : 1.5}
                          strokeDasharray={isClosed ? '4 4' : undefined}
                        />
                        <text x={(x1 + x2) / 2} y={(y1 + y2) / 2 - 4} fill="#8996a6" fontSize="10">{cap}</text>
                      </g>
                    )
                  })}
                  {NODES.map((n) => (
                    <g key={n}>
                      <circle cx={pos[n][0]} cy={pos[n][1]} r={16} fill="#131924" stroke="#1f2733" />
                      <text x={pos[n][0]} y={pos[n][1] + 4} fill="#e6edf3" fontSize="11" textAnchor="middle">{n}</text>
                    </g>
                  ))}
                </>
              )
            })()}
          </svg>
        </div>

        <div className="panel">
          <h2 className="section-title">Evacuation Report</h2>
          {loading && <div className="loading-state">Computing max flow…</div>}
          {error && <div className="error-state">{error}</div>}
          {report && !loading && (
            <div>
              <div className="arena-stat"><span>Scenario</span><span>{report.scenario}</span></div>
              <div className="arena-stat"><span>Max Flow</span><span>{report.max_flow}</span></div>
              <div className="arena-stat">
                <span>Bottleneck Edge</span>
                <span>{report.bottleneck_edge ? `${report.bottleneck_edge[0]} → ${report.bottleneck_edge[1]} (cap ${report.bottleneck_edge[2]})` : 'none'}</span>
              </div>
              <div className="arena-stat"><span>At-Risk Population</span><span>{report.at_risk_population.toLocaleString()}</span></div>
              <div style={{ marginTop: 12 }}>
                <StatusBadge tone={report.max_flow >= 15 ? 'success' : 'warning'}>
                  {report.max_flow >= 15 ? 'network at full capacity' : 'capacity degraded'}
                </StatusBadge>
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-faint)', marginTop: 16 }}>
                Method: Edmonds-Karp (BFS augmenting paths). Critical cut computed from
                residual-graph reachability after max flow converges.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
