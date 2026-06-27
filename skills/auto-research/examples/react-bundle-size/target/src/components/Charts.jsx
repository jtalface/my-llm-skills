// Inline SVG charts — no chart.js or react-chartjs-2 dependency

function BarChart({ labels, data, color = '#3b82f6' }) {
  const max = Math.max(...data, 1)
  const W = 400, H = 180, PAD = 32, barW = Math.floor((W - PAD * 2) / labels.length) - 4

  return (
    <svg viewBox={`0 0 ${W} ${H + 24}`} style={{ width: '100%' }}>
      {data.map((v, i) => {
        const bh = Math.round((v / max) * H)
        const x = PAD + i * (barW + 4)
        return (
          <g key={i}>
            <rect x={x} y={H - bh} width={barW} height={bh} fill={color} rx={2} />
            <text x={x + barW / 2} y={H + 14} textAnchor="middle" fontSize={9} fill="#6b7280">
              {labels[i]}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

function DoughnutChart({ labels, data, colors }) {
  const total = data.reduce((s, v) => s + v, 0) || 1
  const R = 60, cx = 80, cy = 75, stroke = 28
  let angle = -Math.PI / 2
  const arcs = data.map((v, i) => {
    const sweep = (v / total) * 2 * Math.PI
    const x1 = cx + R * Math.cos(angle), y1 = cy + R * Math.sin(angle)
    angle += sweep
    const x2 = cx + R * Math.cos(angle), y2 = cy + R * Math.sin(angle)
    return { x1, y1, x2, y2, sweep, large: sweep > Math.PI ? 1 : 0, color: colors[i], label: labels[i], value: v }
  })

  return (
    <svg viewBox="0 0 180 150" style={{ width: '100%' }}>
      {arcs.map((a, i) => (
        <path key={i}
          d={`M ${a.x1} ${a.y1} A ${R} ${R} 0 ${a.large} 1 ${a.x2} ${a.y2}`}
          fill="none" stroke={a.color} strokeWidth={stroke}
        />
      ))}
      {arcs.map((a, i) => (
        <g key={i}>
          <rect x={125} y={20 + i * 22} width={10} height={10} fill={a.color} rx={2} />
          <text x={138} y={30 + i * 22} fontSize={10} fill="#374151">{a.label} ({a.value})</text>
        </g>
      ))}
    </svg>
  )
}

export default function Charts({ orders }) {
  const byCategory = orders.reduce((acc, o) => { (acc[o.category] = acc[o.category] || []).push(o); return acc }, {})
  const categories = Object.keys(byCategory)
  const revenues   = categories.map(c => byCategory[c].reduce((s, o) => s + o.amount, 0))

  const byStatus = orders.reduce((acc, o) => { acc[o.status] = (acc[o.status] || 0) + 1; return acc }, {})
  const statusLabels = Object.keys(byStatus)
  const statusCounts = statusLabels.map(k => byStatus[k])
  const COLORS = ['#f59e0b', '#3b82f6', '#10b981', '#ef4444']

  return (
    <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
      <div style={{ flex: 2, background: '#fff', borderRadius: 8, padding: '1rem', border: '1px solid #e5e7eb', minWidth: 280 }}>
        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: 8 }}>Revenue by Category</div>
        <BarChart labels={categories} data={revenues} />
      </div>
      <div style={{ flex: 1, background: '#fff', borderRadius: 8, padding: '1rem', border: '1px solid #e5e7eb', minWidth: 200 }}>
        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: 8 }}>Orders by Status</div>
        <DoughnutChart labels={statusLabels} data={statusCounts} colors={COLORS} />
      </div>
    </div>
  )
}
