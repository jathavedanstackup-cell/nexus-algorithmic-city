import { useState } from 'react'
import { SimulationProvider } from './SimulationContext'
import { Overview } from './pages/Overview'
import { Scenarios } from './pages/Scenarios'
import { Arena } from './pages/Arena'
import { Evacuation } from './pages/Evacuation'
import { Benchmarks } from './pages/Benchmarks'
import { Architecture } from './pages/Architecture'

type Page = 'overview' | 'scenarios' | 'arena' | 'evacuation' | 'benchmarks' | 'architecture'

const NAV: { key: Page; label: string }[] = [
  { key: 'overview', label: 'Overview' },
  { key: 'scenarios', label: 'Scenarios' },
  { key: 'arena', label: 'Algorithm Arena' },
  { key: 'evacuation', label: 'Evacuation' },
  { key: 'benchmarks', label: 'Benchmarks' },
  { key: 'architecture', label: 'Architecture' },
]

function App() {
  const [page, setPage] = useState<Page>('overview')

  return (
    <SimulationProvider>
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">
            NEXUS
            <small>SIMULATE · BREAK · BENCHMARK · PROVE</small>
          </div>
          <nav className="nav-list">
            {NAV.map((n) => (
              <button
                key={n.key}
                className={`nav-item ${page === n.key ? 'active' : ''}`}
                onClick={() => setPage(n.key)}
              >
                {n.label}
              </button>
            ))}
          </nav>
          <div style={{ marginTop: 'auto' }}>
            <div className="live-pill"><span className="live-dot" /> SYSTEM LIVE</div>
          </div>
        </aside>
        <main className="main">
          {page === 'overview' && <Overview />}
          {page === 'scenarios' && <Scenarios />}
          {page === 'arena' && <Arena />}
          {page === 'evacuation' && <Evacuation />}
          {page === 'benchmarks' && <Benchmarks />}
          {page === 'architecture' && <Architecture />}
        </main>
      </div>
    </SimulationProvider>
  )
}

export default App
