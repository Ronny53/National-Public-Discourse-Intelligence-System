import type { 
  DashboardSummary, 
  IssueCluster, 
  TrendData, 
  PolicyBrief 
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
  }
}

export default api
