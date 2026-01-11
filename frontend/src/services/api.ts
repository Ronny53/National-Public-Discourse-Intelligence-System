import type { 
  DashboardSummary, 
  IssueCluster, 
  TrendData, 
  PolicyBrief,
  SentimentPrediction,
  RiskPrediction
} from '../types'
import { 
  mockDashboardSummary, 
  mockIssues, 
  mockTrends, 
  mockPolicyBrief 
} from '../data/mockData'

const API_BASE = '/api/v1/dashboard'

async function fetchWithFallback<T>(
  endpoint: string, 
  fallbackData: T
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return await response.json()
  } catch {
    // API unavailable, use mock data
    console.info(`Using mock data for ${endpoint}`)
    return fallbackData
  }
}

export const api = {
  getSummary: (): Promise<DashboardSummary> => 
    fetchWithFallback('/summary', mockDashboardSummary),

  getIssues: (): Promise<IssueCluster[]> => 
    fetchWithFallback('/issues', mockIssues),

  getTrends: (): Promise<TrendData[]> => 
    fetchWithFallback('/trends', mockTrends),

  getBrief: (): Promise<PolicyBrief> => 
    fetchWithFallback('/brief', mockPolicyBrief),

  refresh: async (): Promise<{ status: string; timestamp: string }> => {
    try {
      const response = await fetch(`${API_BASE}/refresh`, { method: 'POST' })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return await response.json()
    } catch {
      return { 
        status: 'refreshed (mock)', 
        timestamp: new Date().toISOString() 
      }
    }
  },

  getSentimentPredictions: (daysAhead: number = 7): Promise<SentimentPrediction> => {
    return fetchWithFallback(`/predictions/sentiment?days_ahead=${daysAhead}`, {
      forecast_dates: [],
      predicted_sentiment: [],
      confidence_upper: [],
      confidence_lower: [],
      trend_direction: 'stable' as const,
      method: 'default',
      note: 'Prediction data unavailable'
    })
  },

  getRiskPredictions: (daysAhead: number = 7): Promise<RiskPrediction> => {
    return fetchWithFallback(`/predictions/risk?days_ahead=${daysAhead}`, {
      predicted_risk: 'medium' as const,
      risk_score: 5.0,
      trend: 'stable' as const,
      confidence: 'low' as const,
      note: 'Prediction data unavailable'
    })
  },

  // Alerts API
  getAlertStatus: async (): Promise<{
    risk_score: number
    risk_level: string
    alert_status: string
    auto_alerts_enabled: boolean
    threshold: number
    last_alert_time: string | null
    can_send_alert: boolean
    time_until_next_alert: number | null
  }> => {
    try {
      const response = await fetch('/api/v1/alerts/status')
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return await response.json()
    } catch {
      return {
        risk_score: 0,
        risk_level: 'Low',
        alert_status: 'Normal',
        auto_alerts_enabled: true,
        threshold: 70,
        last_alert_time: null,
        can_send_alert: true,
        time_until_next_alert: null
      }
    }
  },

  sendManualAlert: async (): Promise<{ status: string; message: string; risk_score: number; timestamp: string }> => {
    try {
      const response = await fetch('/api/v1/alerts/send-manual', { method: 'POST' })
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || `HTTP ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      throw error
    }
  },

  testEmail: async (): Promise<{ status: string; message: string }> => {
    try {
      const response = await fetch('/api/v1/alerts/test-email', { method: 'POST' })
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || `HTTP ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      throw error
    }
  },

  getAlertConfig: async (): Promise<{
    threshold: number
    cooldown_minutes: number
    email_configured: boolean
    recipients: string[]
  }> => {
    try {
      const response = await fetch('/api/v1/alerts/config')
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return await response.json()
    } catch {
      return {
        threshold: 70,
        cooldown_minutes: 15,
        email_configured: false,
        recipients: []
      }
    }
  }
}

export default api
