import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { api } from './api/client'
import type { CitySnapshot, TimelineEvent } from './api/client'

interface SimulationContextValue {
  simId: string | null
  city: CitySnapshot | null
  timeline: TimelineEvent[]
  profile: string
  seed: number
  loading: boolean
  error: string | null
  setProfile: (p: string) => void
  setSeed: (s: number) => void
  rebuild: () => Promise<void>
  refreshCity: () => Promise<void>
  refreshTimeline: () => Promise<void>
}

const SimulationContext = createContext<SimulationContextValue | null>(null)

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [simId, setSimId] = useState<string | null>(null)
  const [city, setCity] = useState<CitySnapshot | null>(null)
  const [timeline, setTimeline] = useState<TimelineEvent[]>([])
  const [profile, setProfile] = useState('medium')
  const [seed, setSeed] = useState(42)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const rebuild = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const snap = await api.createSimulation(profile, seed)
      setSimId(snap.simulation_id)
      setCity(snap.city)
      setTimeline([])
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [profile, seed])

  const refreshCity = useCallback(async () => {
    if (!simId) return
    try {
      const snap = await api.getCity(simId)
      setCity(snap.city)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }, [simId])

  const refreshTimeline = useCallback(async () => {
    if (!simId) return
    try {
      const res = await api.getTimeline(simId)
      setTimeline(res.timeline)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }, [simId])

  useEffect(() => {
    rebuild()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Poll for live updates every 4s once a simulation exists.
  useEffect(() => {
    if (!simId) return
    const id = setInterval(() => {
      refreshCity()
      refreshTimeline()
    }, 4000)
    return () => clearInterval(id)
  }, [simId, refreshCity, refreshTimeline])

  return (
    <SimulationContext.Provider
      value={{ simId, city, timeline, profile, seed, loading, error, setProfile, setSeed, rebuild, refreshCity, refreshTimeline }}
    >
      {children}
    </SimulationContext.Provider>
  )
}

export function useSimulation() {
  const ctx = useContext(SimulationContext)
  if (!ctx) throw new Error('useSimulation must be used within SimulationProvider')
  return ctx
}
