import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from 'recharts'
import type { SentimentPoint } from '../../types'

interface SentimentChartProps {
  data: SentimentPoint[]
}

const COLORS = {
  positive: '#22c55e',
  neutral: '#71717a',
  negative: '#ef4444'
}

interface TooltipProps {
  active?: boolean
  payload?: Array<{
    name: string
    value: number
    color: string
  }>
  label?: string
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload) return null

  return (
    <div className="bg-surface border border-border rounded px-3 py-2 text-xs">
      <p className="text-text-secondary mb-1">{label}</p>
      {payload.map((item) => (
        <div key={item.name} className="flex items-center gap-2 text-text-primary">
          <span 
            className="w-2 h-2 rounded-full" 
            style={{ backgroundColor: item.color }}
          />
          <span className="capitalize">{item.name}:</span>
          <span className="font-mono">{item.value.toFixed(1)}%</span>
        </div>
      ))}
    </div>
  )
}

export default function SentimentChart({ data }: SentimentChartProps) {
  // Format dates for display
  const formattedData = data.map(d => ({
    ...d,
    displayDate: new Date(d.date).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })
  }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart 
        data={formattedData}
        margin={{ top: 10, right: 10, left: -10, bottom: 10 }}
      >
        <CartesianGrid 
          strokeDasharray="3 3" 
          stroke="#1f1f22" 
          vertical={false}
        />
        <XAxis 
          dataKey="displayDate" 
          tick={{ fontSize: 11, fill: '#71717a' }}
          tickLine={false}
          axisLine={{ stroke: '#27272a' }}
          interval="preserveStartEnd"
        />
        <YAxis 
          tick={{ fontSize: 11, fill: '#71717a' }}
          tickLine={false}
          axisLine={false}
          domain={[0, 60]}
          tickFormatter={(v) => `${v}%`}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend 
          wrapperStyle={{ fontSize: 12, paddingTop: 16 }}
          iconType="circle"
          iconSize={8}
        />
        <Line 
          type="monotone" 
          dataKey="positive" 
          stroke={COLORS.positive}
          strokeWidth={1.5}
          dot={false}
          activeDot={{ r: 4, strokeWidth: 0 }}
        />
        <Line 
          type="monotone" 
          dataKey="neutral" 
          stroke={COLORS.neutral}
          strokeWidth={1.5}
          dot={false}
          activeDot={{ r: 4, strokeWidth: 0 }}
        />
        <Line 
          type="monotone" 
          dataKey="negative" 
          stroke={COLORS.negative}
          strokeWidth={1.5}
          dot={false}
          activeDot={{ r: 4, strokeWidth: 0 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
