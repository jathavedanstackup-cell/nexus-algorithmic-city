import { StatusBadge } from './StatusBadge'

interface Props {
  title: string
  description: string
  tone: 'signal' | 'warning' | 'critical' | 'success' | 'dim'
  running?: boolean
  disabled?: boolean
  onRun: () => void
}

export function ScenarioCard({ title, description, tone, running, disabled, onRun }: Props) {
  return (
    <div className="panel scenario-card">
      <StatusBadge tone={tone}>{title}</StatusBadge>
      <h3>{title}</h3>
      <p>{description}</p>
      <button className="btn primary" onClick={onRun} disabled={disabled || running}>
        {running ? 'RUNNING…' : 'RUN SCENARIO'}
      </button>
    </div>
  )
}
