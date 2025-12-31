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
import type { TrendData } from '../../types'

interface TrendChartProps {
  data: TrendData[]
}

// Muted line colors
const LINE_COLORS = [
  '#3b82f6',
  '#22c55e',
  '#f59e0b',
  '#8b5cf6',
  '#ef4444'
]

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
          <span>{item.name}:</span>
          <span className="font-mono">{item.value.toFixed(0)}</span>
        </div>
      ))}
    </div>
  )
}

export default function TrendChart({ data }: TrendChartProps) {
  if (!data || !data.length) {
    return (
      <div className="h-[300px] flex items-center justify-center text-text-muted">
        No trend data available
      </div>
    )
  }

  // Validate data structure
  const validData = data.filter(trend => trend && trend.keyword && trend.data && Array.isArray(trend.data) && trend.data.length > 0)
  
  if (validData.length === 0) {
    return (
      <div className="h-[300px] flex items-center justify-center text-text-muted">
        No valid trend data available
      </div>
    )
  }

  // Transform data for chart: merge all trend lines into single array
  const mergedData = validData[0].data.map((point, idx) => {
    const merged: Record<string, string | number> = {
      date: point.date,
      displayDate: new Date(point.date).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      })
    }
    validData.forEach(trend => {
      merged[trend.keyword] = trend.data[idx]?.value ?? 0
    })
    return merged
  })

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart 
        data={mergedData}
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
          domain={[0, 100]}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend 
          wrapperStyle={{ fontSize: 12, paddingTop: 16 }}
          iconType="circle"
          iconSize={8}
        />
        {validData.map((trend, idx) => (
          <Line 
            key={trend.keyword}
            type="monotone" 
            dataKey={trend.keyword}
            stroke={LINE_COLORS[idx % LINE_COLORS.length]}
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
