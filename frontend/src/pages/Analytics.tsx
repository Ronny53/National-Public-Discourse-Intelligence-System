import { useState, useEffect } from 'react'
import SentimentChart from '../components/charts/SentimentChart'
import EmotionChart from '../components/charts/EmotionChart'
import IntegrityChart from '../components/charts/IntegrityChart'
import TrendChart from '../components/charts/TrendChart'
import api from '../services/api'
import type { DashboardSummary, SentimentPrediction, RiskPrediction } from '../types'
import { mockDashboardSummary, mockSentimentTimeSeries, mockEmotions } from '../data/mockData'

export default function Analytics() {
  const [summary, setSummary] = useState<DashboardSummary>(mockDashboardSummary)
  const [sentimentPrediction, setSentimentPrediction] = useState<SentimentPrediction | null>(null)
  const [riskPrediction, setRiskPrediction] = useState<RiskPrediction | null>(null)
  const [loading, setLoading] = useState(true)
  const [predictionsLoading, setPredictionsLoading] = useState(false)

  useEffect(() => {
    async function fetchData() {
      setLoading(true)
      const result = await api.getSummary()
      setSummary(result)
      setLoading(false)
    }
    fetchData()
  }, [])

  useEffect(() => {
    async function fetchPredictions() {
      setPredictionsLoading(true)
      try {
        const [sentiment, risk] = await Promise.all([
          api.getSentimentPredictions(7),
          api.getRiskPredictions(7)
        ])
        setSentimentPrediction(sentiment)
        setRiskPrediction(risk)
      } catch (error) {
        console.error('Error fetching predictions:', error)
      } finally {
        setPredictionsLoading(false)
      }
    }
    fetchPredictions()
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

      {/* Sentiment Predictions */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-text-primary">Sentiment Forecast</h2>
          <span className="text-xs text-text-muted">Next 7 days prediction</span>
        </div>
        
        <div className="card">
          {predictionsLoading ? (
            <div className="h-[280px] flex items-center justify-center text-text-muted">
              Loading predictions...
            </div>
          ) : sentimentPrediction && sentimentPrediction.forecast_dates.length > 0 ? (
            <div>
              <TrendChart 
                data={[{
                  keyword: 'Predicted Sentiment',
                  data: sentimentPrediction.forecast_dates.map((date, i) => ({
                    date,
                    value: sentimentPrediction.predicted_sentiment[i] * 100 // Scale to 0-100
                  }))
                }]}
              />
              <div className="mt-4 flex items-center gap-4 text-sm">
                <span className={`px-3 py-1 rounded-full ${
                  sentimentPrediction.trend_direction === 'improving' 
                    ? 'bg-green-100 text-green-800' 
                    : sentimentPrediction.trend_direction === 'declining'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  Trend: {sentimentPrediction.trend_direction}
                </span>
                <span className="text-text-muted">
                  Method: {sentimentPrediction.method}
                </span>
              </div>
            </div>
          ) : (
            <div className="h-[280px] flex items-center justify-center text-text-muted">
              {sentimentPrediction?.note || 'Insufficient data for predictions'}
            </div>
          )}
        </div>
        
        <p className="chart-explanation">
          AI-powered forecast of sentiment trends using time-series analysis. Predictions are based on 
          historical patterns and may vary based on data availability. Confidence intervals show prediction uncertainty.
        </p>
      </section>

      {/* Risk Predictions */}
      {riskPrediction && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-text-primary">Escalation Risk Forecast</h2>
            <span className="text-xs text-text-muted">Next 7 days</span>
          </div>
          
          <div className="card">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-secondary">Predicted Risk Level</span>
                <span className={`px-3 py-1 rounded-full font-medium ${
                  riskPrediction.predicted_risk === 'high'
                    ? 'bg-red-100 text-red-800'
                    : riskPrediction.predicted_risk === 'medium'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-green-100 text-green-800'
                }`}>
                  {riskPrediction.predicted_risk.toUpperCase()}
                </span>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary">Risk Score</span>
                  <span className="font-medium">{riskPrediction.risk_score.toFixed(1)}/10</span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      riskPrediction.risk_score >= 7 ? 'bg-red-500' :
                      riskPrediction.risk_score >= 4 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${(riskPrediction.risk_score / 10) * 100}%` }}
                  />
                </div>
              </div>
              
              <div className="flex items-center gap-4 text-sm">
                <span className="text-text-secondary">Trend: </span>
                <span className={`${
                  riskPrediction.trend === 'increasing' ? 'text-red-600' :
                  riskPrediction.trend === 'decreasing' ? 'text-green-600' : 'text-gray-600'
                }`}>
                  {riskPrediction.trend}
                </span>
                <span className="text-text-muted">
                  Confidence: {riskPrediction.confidence}
                </span>
              </div>
              
              {riskPrediction.note && (
                <p className="text-xs text-text-muted italic">{riskPrediction.note}</p>
              )}
            </div>
          </div>
        </section>
      )}

      {/* Methodology Note */}
      <div className="border-t border-border pt-6">
        <h3 className="text-sm font-medium text-text-secondary mb-2">Methodology</h3>
        <p className="text-xs text-text-muted leading-relaxed max-w-2xl">
          Sentiment analysis uses VADER compound scoring. Emotion detection employs NRC lexicon mapping. 
          Integrity metrics are derived from temporal pattern analysis and account clustering algorithms.
          Predictions use time-series forecasting (Prophet/Linear Regression) based on historical sentiment patterns.
          All analysis is performed on ethically-sourced public data only.
        </p>
      </div>
    </div>
  )
}
