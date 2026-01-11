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
  }
}

export default api
