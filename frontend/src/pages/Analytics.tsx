import { useState, useEffect } from 'react'
import SentimentChart from '../components/charts/SentimentChart'
import EmotionChart from '../components/charts/EmotionChart'
import IntegrityChart from '../components/charts/IntegrityChart'
import api from '../services/api'
import type { DashboardSummary } from '../types'
import { mockDashboardSummary, mockSentimentTimeSeries, mockEmotions } from '../data/mockData'

export default function Analytics() {
  const [summary, setSummary] = useState<DashboardSummary>(mockDashboardSummary)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      setLoading(true)
      const result = await api.getSummary()
      setSummary(result)
      setLoading(false)
    }
    fetchData()
  }, [])

  return (
    <div className="space-y-10">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Analytics</h1>
        <p className="text-sm text-text-muted mt-1">
          Detailed sentiment and emotion analysis
        </p>
      </div>

      {/* Sentiment Over Time */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-text-primary">Sentiment Over Time</h2>
          <span className="text-xs text-text-muted">Last 30 days</span>
        </div>
        
        <div className="card">
          {loading ? (
            <div className="h-[280px] flex items-center justify-center text-text-muted">
              Loading...
            </div>
          ) : (
            <SentimentChart data={mockSentimentTimeSeries} />
          )}
        </div>
        
        <p className="chart-explanation">
          Tracks the distribution of positive, neutral, and negative sentiment across analyzed content. 
          Higher positive ratios correlate with improved Trust Index scores.
        </p>
      </section>

      {/* Emotion Distribution */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-text-primary">Emotion Distribution</h2>
          <span className="text-xs text-text-muted">Aggregate density</span>
        </div>
        
        <div className="card">
          {loading ? (
            <div className="h-[280px] flex items-center justify-center text-text-muted">
              Loading...
            </div>
          ) : (
            <EmotionChart data={mockEmotions} />
          )}
        </div>
        
        <p className="chart-explanation">
          Shows the emotional composition of public discourse. High-arousal emotions (anger, fear) 
          are key drivers of escalation risk, while trust and anticipation indicate constructive engagement.
        </p>
      </section>

      {/* Integrity Classification */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-text-primary">Integrity Classification</h2>
          <span className="text-xs text-text-muted">Detection scores</span>
        </div>
        
        <div className="card">
          {loading ? (
            <div className="h-[120px] flex items-center justify-center text-text-muted">
              Loading...
            </div>
          ) : (
            <IntegrityChart 
              amplificationScore={summary.integrity_metrics.amplification.amplification_score}
              coordinationScore={summary.integrity_metrics.coordination.burst_score}
            />
          )}
        </div>
        
        <p className="chart-explanation">
          Measures potential inauthentic activity. Amplification detects artificial boosting patterns; 
          Coordination identifies synchronized posting behavior suggestive of organized campaigns.
        </p>
      </section>

      {/* Methodology Note */}
      <div className="border-t border-border pt-6">
        <h3 className="text-sm font-medium text-text-secondary mb-2">Methodology</h3>
        <p className="text-xs text-text-muted leading-relaxed max-w-2xl">
          Sentiment analysis uses VADER compound scoring. Emotion detection employs NRC lexicon mapping. 
          Integrity metrics are derived from temporal pattern analysis and account clustering algorithms. 
          All analysis is performed on ethically-sourced public data only.
        </p>
      </div>
    </div>
  )
}
