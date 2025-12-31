import { useState, useEffect } from 'react'
import MetricCard from '../components/MetricCard'
import api from '../services/api'
import type { DashboardSummary } from '../types'
import { mockDashboardSummary } from '../data/mockData'

function getRiskStatus(level: string): 'success' | 'warning' | 'danger' {
  switch (level) {
    case 'Low': return 'success'
    case 'Moderate': return 'warning'
    case 'High':
    case 'Critical': return 'danger'
    default: return 'success'
  }
}

function getTrustStatus(value: number): 'success' | 'warning' | 'danger' {
  if (value >= 70) return 'success'
  if (value >= 50) return 'warning'
  return 'danger'
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary>(mockDashboardSummary)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  useEffect(() => {
    async function fetchData() {
      setLoading(true)
      const result = await api.getSummary()
      setData(result)
      setLastUpdated(new Date())
      setLoading(false)
    }
    fetchData()
  }, [])

  const riskLevel = data.escalation_risk.level
  const riskScore = data.escalation_risk.score

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">National Pulse</h1>
          <p className="text-sm text-text-muted mt-1">
            Real-time public discourse analytics
          </p>
        </div>
        <div className="text-xs text-text-muted">
          {loading ? (
            <span>Updating...</span>
          ) : (
            <span>Updated {lastUpdated.toLocaleTimeString()}</span>
          )}
        </div>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-3 gap-8 border-b border-border pb-8">
        <MetricCard
          label="Trust Index"
          value={data.trust_index.toFixed(1)}
          subValue="/ 100"
          status={getTrustStatus(data.trust_index)}
          trend={{ direction: 'up', value: '+2.3' }}
          explanation="Composite measure of sentiment balance, discourse integrity, and civility across analyzed content."
        />
        
        <MetricCard
          label="Risk Level"
          value={riskLevel}
          subValue={`${riskScore.toFixed(1)}`}
          status={getRiskStatus(riskLevel)}
          trend={{ direction: 'stable', value: '—' }}
          explanation="Escalation risk based on negativity, emotional arousal, and discussion momentum patterns."
        />

        <MetricCard
          label="Volatility Index"
          value={data.volatility_index.toFixed(1)}
          subValue="/ 100"
          status={data.volatility_index < 40 ? 'success' : data.volatility_index < 60 ? 'warning' : 'danger'}
          trend={{ direction: 'down', value: '-1.8' }}
          explanation="Measure of sentiment variance over time. Lower values indicate stable public opinion."
        />
      </div>

      {/* Risk Drivers */}
      <div>
        <h2 className="section-title mb-4">Risk Drivers</h2>
        <div className="grid grid-cols-3 gap-6">
          <div className="py-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-text-secondary">Negativity</span>
              <span className="text-sm font-mono text-text-primary">
                {(data.escalation_risk.drivers.negativity * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-1.5 bg-surface rounded-full overflow-hidden">
              <div 
                className="h-full bg-danger rounded-full transition-all duration-500"
                style={{ width: `${data.escalation_risk.drivers.negativity * 100}%` }}
              />
            </div>
          </div>

          <div className="py-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-text-secondary">Emotional Arousal</span>
              <span className="text-sm font-mono text-text-primary">
                {(data.escalation_risk.drivers.arousal * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-1.5 bg-surface rounded-full overflow-hidden">
              <div 
                className="h-full bg-warning rounded-full transition-all duration-500"
                style={{ width: `${data.escalation_risk.drivers.arousal * 100}%` }}
              />
            </div>
          </div>

          <div className="py-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-text-secondary">Momentum</span>
              <span className="text-sm font-mono text-text-primary">
                {(data.escalation_risk.drivers.momentum * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-1.5 bg-surface rounded-full overflow-hidden">
              <div 
                className="h-full bg-accent rounded-full transition-all duration-500"
                style={{ width: `${data.escalation_risk.drivers.momentum * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Integrity Metrics */}
      <div className="border-t border-border pt-8">
        <h2 className="section-title mb-4">Integrity Metrics</h2>
        <div className="grid grid-cols-2 gap-6">
          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-text-primary">Amplification Detection</span>
              <span className="text-xs text-text-muted">
                {data.integrity_metrics.amplification.detected_campaigns} campaigns detected
              </span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-xl font-semibold text-text-primary">
                {(data.integrity_metrics.amplification.amplification_score * 100).toFixed(1)}%
              </span>
              <span className="text-xs text-text-muted">amplification score</span>
            </div>
            <p className="text-xs text-text-muted mt-2">
              Measures coordinated inauthentic behavior and artificial boosting patterns.
            </p>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-text-primary">Coordination Detection</span>
              <span className="text-xs text-text-muted">
                {data.integrity_metrics.coordination.detected_bursts} bursts detected
              </span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-xl font-semibold text-text-primary">
                {(data.integrity_metrics.coordination.burst_score * 100).toFixed(1)}%
              </span>
              <span className="text-xs text-text-muted">burst score</span>
            </div>
            <p className="text-xs text-text-muted mt-2">
              Tracks sudden coordinated activity spikes suggesting organized campaigns.
            </p>
          </div>
        </div>
      </div>

      {/* Footer Stats */}
      <div className="border-t border-border pt-6 flex items-center justify-between text-xs text-text-muted">
        <span>Total posts analyzed: {data.total_posts_analyzed.toLocaleString()}</span>
        <span>Demo data • Backend API not connected</span>
      </div>
    </div>
  )
}
