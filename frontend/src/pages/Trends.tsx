import { useState, useEffect } from 'react'
import TrendChart from '../components/charts/TrendChart'
import DataTable from '../components/DataTable'
import api from '../services/api'
import type { IssueCluster, TrendData } from '../types'
import { mockIssues, mockTrends } from '../data/mockData'

const trendBadge = {
  rising: { label: 'Rising', color: 'text-success bg-success/10' },
  stable: { label: 'Stable', color: 'text-text-muted bg-surface' },
  declining: { label: 'Declining', color: 'text-danger bg-danger/10' }
}

export default function Trends() {
  const [issues, setIssues] = useState<IssueCluster[]>(mockIssues)
  const [trends, setTrends] = useState<TrendData[]>(mockTrends)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      setLoading(true)
      const [issuesRes, trendsRes] = await Promise.all([
        api.getIssues(),
        api.getTrends()
      ])
      setIssues(issuesRes)
      setTrends(trendsRes)
      setLoading(false)
    }
    fetchData()
  }, [])

  const columns = [
    { 
      key: 'label', 
      label: 'Issue',
      render: (row: IssueCluster) => (
        <span className="font-medium text-text-primary">{row.label}</span>
      )
    },
    {
      key: 'top_keywords',
      label: 'Keywords',
      render: (row: IssueCluster) => (
        <div className="flex gap-1.5 flex-wrap">
          {row.top_keywords.slice(0, 3).map(kw => (
            <span key={kw} className="text-xs px-1.5 py-0.5 bg-surface rounded text-text-muted">
              {kw}
            </span>
          ))}
        </div>
      )
    },
    {
      key: 'post_count',
      label: 'Volume',
      render: (row: IssueCluster) => (
        <span className="font-mono text-text-secondary">{row.post_count}</span>
      )
    },
    {
      key: 'avg_sentiment',
      label: 'Sentiment',
      render: (row: IssueCluster) => {
        const value = row.avg_sentiment
        const color = value > 0.2 ? 'text-success' : value < -0.1 ? 'text-danger' : 'text-text-muted'
        return (
          <span className={`font-mono ${color}`}>
            {value > 0 ? '+' : ''}{value.toFixed(2)}
          </span>
        )
      }
    },
    {
      key: 'trend',
      label: 'Trend',
      render: (row: IssueCluster) => {
        const badge = trendBadge[row.trend]
        return (
          <span className={`text-xs px-2 py-0.5 rounded ${badge.color}`}>
            {badge.label}
          </span>
        )
      }
    }
  ]

  return (
    <div className="space-y-10">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Trends</h1>
        <p className="text-sm text-text-muted mt-1">
          Issue tracking and keyword interest over time
        </p>
      </div>

      {/* Trend Chart */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-text-primary">Interest Over Time</h2>
          <span className="text-xs text-text-muted">Top keywords • 30 days</span>
        </div>
        
        <div className="card">
          {loading ? (
            <div className="h-[300px] flex items-center justify-center text-text-muted">
              Loading...
            </div>
          ) : (
            <TrendChart data={trends} />
          )}
        </div>
        
        <p className="chart-explanation">
          Tracks relative search and discussion interest for top keywords extracted from issue clusters. 
          Useful for identifying emerging topics before they reach critical volume.
        </p>
      </section>

      {/* Issues Table */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-text-primary">Active Issues</h2>
          <span className="text-xs text-text-muted">{issues.length} clusters identified</span>
        </div>
        
        <div className="card p-0 overflow-hidden">
          {loading ? (
            <div className="h-[200px] flex items-center justify-center text-text-muted">
              Loading...
            </div>
          ) : (
            <DataTable 
              columns={columns}
              data={issues}
              keyField="label"
            />
          )}
        </div>
        
        <p className="chart-explanation">
          Issues are automatically clustered from analyzed content using topic modeling. 
          Sentiment reflects aggregate public opinion; trend indicates volume trajectory.
        </p>
      </section>
    </div>
  )
}
