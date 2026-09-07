import { useState } from 'react'
import { api } from '../api/client'
import type { BenchmarkRecord } from '../api/client'

const PROFILES = ['small', 'medium', 'large', 'stress']

export function Benchmarks() {
  const [profile, setProfile] = useState('small')
  const [seed, setSeed] = useState(42)
  const [records, setRecords] = useState<BenchmarkRecord[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function run() {
    setLoading(true)
    setError(null)
    try {
      const res = await api.postBenchmark(profile, seed)
      setRecords(res.records)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Benchmarks</h1>
          <p>Real, measured runtime/memory/quality numbers. Never fabricated.</p>
        </div>
      </div>

      <div className="panel" style={{ marginBottom: 24 }}>
        <div className="controls-row">
          <label style={{ fontSize: 12, color: 'var(--text-dim)' }}>Profile</label>
          <select value={profile} onChange={(e) => setProfile(e.target.value)}>
            {PROFILES.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <label style={{ fontSize: 12, color: 'var(--text-dim)' }}>Seed</label>
          <input type="number" value={seed} onChange={(e) => setSeed(Number(e.target.value))} style={{ width: 90 }} />
          <button className="btn primary" onClick={run} disabled={loading}>
            {loading ? 'RUNNING…' : 'RUN BENCHMARK'}
          </button>
        </div>
        {profile === 'stress' && (
          <p style={{ fontSize: 12, color: 'var(--warning)' }}>
            Stress profile is capped at 50,000 nodes (documented sandbox limit) rather than 100,000 — may take several seconds.
          </p>
        )}
        {error && <div className="error-state">{error}</div>}
      </div>

      {records && (
        <div className="panel" style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: 'var(--mono)', fontSize: 12.5 }}>
            <thead>
              <tr style={{ textAlign: 'left', color: 'var(--text-dim)' }}>
                <th style={{ padding: 8 }}>Algorithm</th>
                <th style={{ padding: 8 }}>Input Size</th>
                <th style={{ padding: 8 }}>Runtime (ms)</th>
                <th style={{ padding: 8 }}>Nodes Explored</th>
                <th style={{ padding: 8 }}>Edge Relaxations</th>
                <th style={{ padding: 8 }}>Path Cost</th>
                <th style={{ padding: 8 }}>Memory (KB)</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r, i) => (
                <tr key={i} style={{ borderTop: '1px solid var(--border)' }}>
                  <td style={{ padding: 8 }}>{r.algorithm}</td>
                  <td style={{ padding: 8 }}>{r.input_size}</td>
                  <td style={{ padding: 8 }}>{r.runtime_ms.toFixed(3)}</td>
                  <td style={{ padding: 8 }}>{r.nodes_explored}</td>
                  <td style={{ padding: 8 }}>{r.edge_relaxations}</td>
                  <td style={{ padding: 8 }}>{r.path_found ? r.path_cost.toFixed(2) : 'no path'}</td>
                  <td style={{ padding: 8 }}>{r.memory_kb}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p style={{ fontSize: 11, color: 'var(--text-faint)', marginTop: 12 }}>
            Machine: {records[0]?.machine} · Results also persisted server-side to benchmarks/results/.
          </p>
        </div>
      )}
      {!records && !loading && <div className="empty-state">Run a benchmark to see real measurements.</div>}
    </div>
  )
}
