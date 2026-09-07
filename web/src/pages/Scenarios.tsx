import { useState } from 'react'
import { ScenarioCard } from '../components/ScenarioCard'
import { EventTimeline } from '../components/EventTimeline'
import { TelemetryPanel } from '../components/TelemetryPanel'
import { useSimulation } from '../SimulationContext'
import { api } from '../api/client'
import type { DispatchTelemetry } from '../api/client'

const SCENARIOS: { key: string; title: string; description: string; zone?: string; tone: 'signal' | 'warning' | 'critical' | 'success' | 'dim' }[] = [
  { key: 'fire', title: 'Fire', description: 'Industrial zone fire. Triggers priority-queue unit search and A* routing.', zone: 'industrial_1', tone: 'critical' },
  { key: 'flood', title: 'Flood', description: 'North district flood. Closes multiple roads simultaneously.', zone: 'north_district', tone: 'signal' },
  { key: 'road_failure', title: 'Bridge Closure', description: 'Forces dynamic route recalculation around a closed edge.', tone: 'warning' },
  { key: 'power_failure', title: 'Power Failure', description: 'District 7 loses power, affecting nearby facilities.', zone: 'district_7', tone: 'warning' },
  { key: 'multi', title: 'Multi-Incident', description: 'Fire and flood triggered simultaneously across zones.', tone: 'critical' },
  { key: 'chaos', title: 'Chaos', description: 'Adversarial composition of failures. Deterministic per seed, never crashes.', tone: 'critical' },
]

export function Scenarios() {
  const { simId, timeline, refreshTimeline, refreshCity, seed } = useSimulation()
  const [running, setRunning] = useState<string | null>(null)
  const [lastIncidentId, setLastIncidentId] = useState<string | null>(null)
  const [dispatch, setDispatch] = useState<DispatchTelemetry | null>(null)
  const [dispatchLoading, setDispatchLoading] = useState(false)
  const [dispatchError, setDispatchError] = useState<string | null>(null)
  const [chaosLog, setChaosLog] = useState<string[] | null>(null)

  async function run(key: string, zone?: string) {
    if (!simId) return
    setRunning(key)
    setDispatchError(null)
    try {
      if (key === 'chaos') {
        const report = await api.postChaos(simId, seed)
        setChaosLog(report.actions.concat(report.graceful_failures.map((g) => `graceful: ${g}`)))
      } else if (key === 'multi') {
        const r1 = await api.postEvent(simId, 'fire', 'industrial_1') as { event: { data: { incident_id: string } } }
        await api.postEvent(simId, 'flood', 'north_district')
        setLastIncidentId(r1.event.data.incident_id)
      } else {
        const res = await api.postEvent(simId, key, zone) as { event: { data: { incident_id: string } } }
        setLastIncidentId(res.event.data.incident_id)
      }
      await refreshTimeline()
      await refreshCity()
    } catch (e) {
      setDispatchError(e instanceof Error ? e.message : String(e))
    } finally {
      setRunning(null)
    }
  }

  async function dispatchNow() {
    if (!simId || !lastIncidentId) return
    setDispatchLoading(true)
    setDispatchError(null)
    try {
      const res = await api.getDispatch(simId, lastIncidentId)
      setDispatch(res)
    } catch (e) {
      setDispatchError(e instanceof Error ? e.message : String(e))
    } finally {
      setDispatchLoading(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Scenario Launcher</h1>
          <p>Trigger disasters against the live city. Every scenario supports a deterministic seed.</p>
        </div>
      </div>

      <div className="grid grid-3" style={{ marginBottom: 24 }}>
        {SCENARIOS.map((s) => (
          <ScenarioCard
            key={s.key}
            title={s.title}
            description={s.description}
            tone={s.tone}
            running={running === s.key}
            disabled={!simId}
            onRun={() => run(s.key, s.zone)}
          />
        ))}
      </div>

      <div className="grid grid-2">
        <div className="panel">
          <h2 className="section-title">Emergency Response Pipeline</h2>
          <div className="controls-row">
            <button className="btn primary" onClick={dispatchNow} disabled={!lastIncidentId || dispatchLoading}>
              {dispatchLoading ? 'DISPATCHING…' : 'RUN DISPATCH ON LATEST INCIDENT'}
            </button>
            {lastIncidentId && <span className="badge dim">{lastIncidentId}</span>}
          </div>
          <TelemetryPanel data={dispatch} loading={dispatchLoading} error={dispatchError} />
          {chaosLog && (
            <div style={{ marginTop: 16 }}>
              <h2 className="section-title">Chaos Log</h2>
              <div className="stage-list">
                {chaosLog.map((line, i) => <div className="stage-item" key={i}>{line}</div>)}
              </div>
            </div>
          )}
        </div>
        <div className="panel">
          <h2 className="section-title">Event Timeline</h2>
          <EventTimeline events={timeline} />
        </div>
      </div>
    </div>
  )
}
