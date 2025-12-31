import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts'

interface IntegrityChartProps {
  amplificationScore: number
  coordinationScore: number
}

interface TooltipProps {
  active?: boolean
  payload?: Array<{
    payload: { name: string; value: number; fill: string }
  }>
}

function CustomTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null

  const item = payload[0].payload
  return (
    <div className="bg-surface border border-border rounded px-3 py-2 text-xs">
      <div className="flex items-center gap-2 text-text-primary">
        <span>{item.name}:</span>
        <span className="font-mono">{(item.value * 100).toFixed(1)}%</span>
      </div>
    </div>
  )
}

export default function IntegrityChart({ amplificationScore, coordinationScore }: IntegrityChartProps) {
  const data = [
    { name: 'Amplification', value: amplificationScore, fill: '#f59e0b' },
    { name: 'Coordination', value: coordinationScore, fill: '#8b5cf6' }
  ]

  return (
    <ResponsiveContainer width="100%" height={120}>
      <BarChart 
        data={data}
        layout="vertical"
        margin={{ top: 10, right: 20, left: 80, bottom: 10 }}
      >
        <XAxis 
          type="number"
          tick={{ fontSize: 11, fill: '#71717a' }}
          tickLine={false}
          axisLine={{ stroke: '#27272a' }}
          domain={[0, 1]}
          tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
        />
        <YAxis 
          type="category"
          dataKey="name"
          tick={{ fontSize: 11, fill: '#a1a1aa' }}
          tickLine={false}
          axisLine={false}
          width={90}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#1f1f22' }} />
        <Bar 
          dataKey="value" 
          radius={[0, 2, 2, 0]}
          maxBarSize={16}
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
