import type { 
  DashboardSummary, 
  IssueCluster, 
  TrendData, 
  PolicyBrief, 
  SentimentPoint, 
  EmotionData 
} from '../types'

// Generate dates for the last N days
function generateDates(days: number): string[] {
  const dates: string[] = []
  const today = new Date()
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])
  }
  return dates
}

// Generate realistic sentiment time series
function generateSentimentData(days: number): SentimentPoint[] {
  const dates = generateDates(days)
  return dates.map((date, i) => {
    // Create some variation with a slight trend
    const base = 0.55 + Math.sin(i / 5) * 0.1
    const positive = Math.max(0.15, Math.min(0.45, base + (Math.random() - 0.5) * 0.1))
    const negative = Math.max(0.1, Math.min(0.35, 0.25 + (Math.random() - 0.5) * 0.1))
    const neutral = 1 - positive - negative
    const compound = (positive - negative) / (positive + negative + 0.001)
    
    return {
      date,
      positive: Number((positive * 100).toFixed(1)),
      neutral: Number((neutral * 100).toFixed(1)),
      negative: Number((negative * 100).toFixed(1)),
      compound: Number(compound.toFixed(3))
    }
  })
}

// Mock Dashboard Summary
export const mockDashboardSummary: DashboardSummary = {
  trust_index: 72.4,
  volatility_index: 34.2,
  escalation_risk: {
    score: 28.5,
    level: 'Low',
    drivers: {
      negativity: 0.22,
      arousal: 0.18,
      momentum: 0.31
    }
  },
  integrity_metrics: {
    amplification: {
      amplification_score: 0.12,
      detected_campaigns: 2
    },
    coordination: {
      burst_score: 0.08,
      detected_bursts: 1
    }
  },
  total_posts_analyzed: 847
}

// Mock Issue Clusters
export const mockIssues: IssueCluster[] = [
  {
    label: 'Infrastructure Development',
    top_keywords: ['roads', 'highways', 'construction', 'transport'],
    post_count: 156,
    avg_sentiment: 0.42,
    trend: 'rising'
  },
  {
    label: 'Digital Payments',
    top_keywords: ['upi', 'payment', 'banking', 'digital'],
    post_count: 134,
    avg_sentiment: 0.68,
    trend: 'stable'
  },
  {
    label: 'Education Policy',
    top_keywords: ['education', 'schools', 'nep', 'students'],
    post_count: 98,
    avg_sentiment: 0.35,
    trend: 'declining'
  },
  {
    label: 'Environmental Concerns',
    top_keywords: ['pollution', 'climate', 'environment', 'water'],
    post_count: 87,
    avg_sentiment: -0.15,
    trend: 'rising'
  },
  {
    label: 'Healthcare Access',
    top_keywords: ['health', 'hospital', 'medicine', 'doctors'],
    post_count: 76,
    avg_sentiment: 0.28,
    trend: 'stable'
  }
]

// Mock Trend Data
export const mockTrends: TrendData[] = [
  {
    keyword: 'Infrastructure',
    data: generateDates(30).map((date, i) => ({
      date,
      value: 45 + Math.sin(i / 4) * 15 + Math.random() * 10
    }))
  },
  {
    keyword: 'Digital Payment',
    data: generateDates(30).map((date, i) => ({
      date,
      value: 60 + Math.cos(i / 3) * 12 + Math.random() * 8
    }))
  },
  {
    keyword: 'Education',
    data: generateDates(30).map((date, i) => ({
      date,
      value: 35 + Math.sin(i / 5 + 1) * 10 + Math.random() * 12
    }))
  }
]

// Mock Policy Brief
export const mockPolicyBrief: PolicyBrief = {
  executive_summary: `National discourse risk is currently Low (Score: 28.5). Trust Index is 72.4. The discourse landscape shows generally positive engagement with government initiatives, particularly in digital infrastructure and payments. Environmental concerns are showing increased activity with slightly negative sentiment, warranting monitoring. Primary drivers of current risk levels are moderate momentum in new discussions (0.31) coupled with low negativity (0.22) and minimal emotional arousal (0.18).`,
  recommended_actions: [
    'Monitor: Maintain surveillance on emerging environmental discourse patterns.',
    'Engage: Consider proactive communication on infrastructure project timelines.',
    'Amplify: Leverage positive digital payments sentiment for financial inclusion messaging.',
    'Research: Deep-dive into education policy concerns to identify specific pain points.'
  ],
  responsible_ministries: [
    'Ministry of Road Transport and Highways',
    'Ministry of Finance / RBI',
    'Ministry of Education',
    'Ministry of Environment, Forest and Climate Change',
    'MeitY'
  ],
  generated_at: new Date().toISOString()
}

// Mock Sentiment Time Series
export const mockSentimentTimeSeries: SentimentPoint[] = generateSentimentData(30)

// Mock Emotion Distribution
export const mockEmotions: EmotionData[] = [
  { emotion: 'Trust', value: 0.32 },
  { emotion: 'Anticipation', value: 0.24 },
  { emotion: 'Joy', value: 0.18 },
  { emotion: 'Surprise', value: 0.08 },
  { emotion: 'Fear', value: 0.07 },
  { emotion: 'Sadness', value: 0.06 },
  { emotion: 'Anger', value: 0.04 },
  { emotion: 'Disgust', value: 0.01 }
]
