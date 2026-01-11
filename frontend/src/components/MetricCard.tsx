import type { ReactNode } from 'react'

interface MetricCardProps {
  label: string
  value: string | number
  subValue?: string
  trend?: {
    direction: 'up' | 'down' | 'stable'
    value: string
  }
  status?: 'default' | 'success' | 'warning' | 'danger'
  explanation?: string
  children?: ReactNode
}

export default function MetricCard({ 
  label, 
  value, 
  subValue,
  trend,
  status = 'default',
  explanation,
  children
}: MetricCardProps) {
  const statusColors = {
    default: 'text-text-primary',
    success: 'text-success',
    warning: 'text-warning',
    danger: 'text-danger'
  }

  const trendColors = {
    up: 'text-success',
    down: 'text-danger',
    stable: 'text-text-muted'
  }

  const trendIcons = {
    up: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l5-5 5 5" />
      </svg>
    ),
    down: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 7l-5 5-5-5" />
      </svg>
    ),
    stable: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
      </svg>
    )
  }

  return (
    <div className="py-5 px-5 border border-border rounded-md">
      <div className="flex items-start justify-between mb-2">
        <span className="metric-label">{label}</span>
        {trend && (
          <div className={`flex items-center gap-1 text-xs ${trendColors[trend.direction]}`}>
            {trendIcons[trend.direction]}
            <span>{trend.value}</span>
          </div>
        )}
      </div>
      
      <div className="flex items-baseline gap-2">
        <span className={`metric-value ${statusColors[status]}`}>
          {value}
        </span>
        {subValue && (
          <span className="text-sm text-text-muted">
            {subValue}
          </span>
        )}
      </div>

      {explanation && (
        <p className="text-xs text-text-muted mt-2 leading-relaxed">
          {explanation}
        </p>
      )}

      {children}
    </div>
  )
}
