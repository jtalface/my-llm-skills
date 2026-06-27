// Stat card
function Card({ label, value }) {
  return (
    <div style={{
      background: '#fff', borderRadius: 8, padding: '1rem 1.25rem',
      border: '1px solid #e5e7eb', flex: 1,
    }}>
      <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>{value}</div>
    </div>
  )
}

export default function Dashboard({ stats }) {
  const revenue = `$${Math.round(stats.revenue * 100) / 100}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  const avg     = `$${(Math.round(stats.avgOrder * 100) / 100).toFixed(2)}`

  return (
    <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
      <Card label="Total Orders"    value={stats.total} />
      <Card label="Total Revenue"   value={revenue} />
      <Card label="Average Order"   value={avg} />
      <Card label="Pending"         value={stats.byStatus.pending || 0} />
      <Card label="Delivered"       value={stats.byStatus.delivered || 0} />
    </div>
  )
}
