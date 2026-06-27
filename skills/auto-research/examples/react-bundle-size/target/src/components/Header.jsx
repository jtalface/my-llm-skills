export default function Header() {
  const formatted = new Date().toLocaleString('en-US', {
    month: 'long', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit', hour12: true,
  })
  return (
    <div style={{ padding: '1rem 0', borderBottom: '1px solid #e5e7eb', marginBottom: '1.5rem' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Analytics Dashboard</h1>
      <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
        As of {formatted}
      </p>
    </div>
  )
}
