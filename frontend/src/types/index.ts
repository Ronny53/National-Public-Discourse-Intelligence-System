// Dashboard Summary Types
export interface EscalationRiskDrivers {
  negativity: number
  arousal: number
  momentum: number
}

export interface EscalationRisk {
  score: number
  level: 'Low' | 'Moderate' | 'High' | 'Critical'
  drivers: EscalationRiskDrivers
}

export interface AmplificationMetrics {
  amplification_score: number
  detected_campaigns: number
}

export interface CoordinationMetrics {
  burst_score: number
  detected_bursts: number
}

export interface IntegrityMetrics {
  amplification: AmplificationMetrics
  coordination: CoordinationMetrics
}

export interface DashboardSummary {
  trust_index: number
  volatility_index: number
  escalation_risk: EscalationRisk
  integrity_metrics: IntegrityMetrics
  total_posts_analyzed: number
}

// Issue Cluster Types
export interface IssueCluster {
  label: string
  top_keywords: string[]
  post_count: number
  avg_sentiment: number
  trend: 'rising' | 'stable' | 'declining'
}

// Trend Data Types
export interface TrendPoint {
  date: string
  value: number
}

export interface TrendData {
  keyword: string
  data: TrendPoint[]
}

// Policy Brief Types
export interface PolicyBrief {
  executive_summary: string
  recommended_actions: string[]
  responsible_ministries: string[]
  generated_at: string
}

// Analytics Data Types
export interface SentimentPoint {
  date: string
  positive: number
  neutral: number
  negative: number
  compound: number
}

export interface EmotionData {
  emotion: string
  value: number
}

// API Response wrapper
export interface ApiResponse<T> {
  data: T | null
  error: string | null
  isLoading: boolean
}
