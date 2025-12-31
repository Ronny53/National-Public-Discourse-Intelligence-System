import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts'
import type { EmotionData } from '../../types'

interface EmotionChartProps {
  data: EmotionData[]
}

// Muted color palette for emotions
const EMOTION_COLORS: Record<string, string> = {
  'Trust': '#3b82f6',
  'Anticipation': '#8b5cf6',
  'Joy': '#22c55e',
  'Surprise': '#f59e0b',
  'Fear': '#ef4444',
  'Sadness': '#64748b',
  'Anger': '#dc2626',
  'Disgust': '#71717a'
}

interface TooltipProps {
  active?: boolean
  payload?: Array<{
    payload: EmotionData
  }>
}

function CustomTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null

  const item = payload[0].payload
  return (
    <div className="bg-surface border border-border rounded px-3 py-2 text-xs">
      <div className="flex items-center gap-2 text-text-primary">
        <span>{item.emotion}:</span>
        <span className="font-mono">{(item.value * 100).toFixed(1)}%</span>
      </div>
    </div>
  )
}

export default function EmotionChart({ data }: EmotionChartProps) {
  // Sort by value descending
  const sortedData = [...data].sort((a, b) => b.value - a.value)

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart 
        data={sortedData}
        layout="vertical"
        margin={{ top: 10, right: 20, left: 60, bottom: 10 }}
      >
        <XAxis 
          type="number"
          tick={{ fontSize: 11, fill: '#71717a' }}
          tickLine={false}
          axisLine={{ stroke: '#27272a' }}
          domain={[0, 0.4]}
          tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
        />
        <YAxis 
          type="category"
          dataKey="emotion"
          tick={{ fontSize: 11, fill: '#a1a1aa' }}
          tickLine={false}
          axisLine={false}
          width={70}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#1f1f22' }} />
        <Bar 
          dataKey="value" 
          radius={[0, 2, 2, 0]}
          maxBarSize={20}
        >
          {sortedData.map((entry) => (
            <Cell 
              key={entry.emotion} 
              fill={EMOTION_COLORS[entry.emotion] || '#71717a'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
