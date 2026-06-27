const fmt = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' })

const COLS = [
  { key: 'customer', label: 'Customer' },
  { key: 'product',  label: 'Product' },
  { key: 'category', label: 'Category' },
  { key: 'amount',   label: 'Amount' },
  { key: 'status',   label: 'Status' },
  { key: 'date',     label: 'Date' },
]

const STATUS_COLORS = {
  pending:   '#f59e0b',
  shipped:   '#3b82f6',
  delivered: '#10b981',
  cancelled: '#ef4444',
}

export default function DataTable({ orders, onSort, sortKey }) {
  return (
    <div style={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb', overflow: 'hidden' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
        <thead>
          <tr style={{ background: '#f9fafb' }}>
            {COLS.map(c => (
              <th
                key={c.key}
                onClick={() => onSort(c.key)}
                style={{
                  padding: '0.75rem 1rem', textAlign: 'left', fontWeight: 500,
                  cursor: 'pointer', borderBottom: '1px solid #e5e7eb',
                  color: sortKey === c.key ? '#3b82f6' : '#374151',
                }}
              >
                {c.label} {sortKey === c.key ? '↑' : ''}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {orders.slice(0, 50).map((o, i) => (
            <tr key={o.id} style={{ borderBottom: '1px solid #f3f4f6', background: i % 2 ? '#fafafa' : '#fff' }}>
              <td style={{ padding: '0.6rem 1rem' }}>{o.customer}</td>
              <td style={{ padding: '0.6rem 1rem' }}>{o.product}</td>
              <td style={{ padding: '0.6rem 1rem' }}>{o.category}</td>
              <td style={{ padding: '0.6rem 1rem' }}>${(Math.round(o.amount * 100) / 100).toFixed(2)}</td>
              <td style={{ padding: '0.6rem 1rem' }}>
                <span style={{
                  background: STATUS_COLORS[o.status] + '22',
                  color: STATUS_COLORS[o.status],
                  padding: '2px 8px', borderRadius: 12, fontSize: '0.75rem', fontWeight: 500,
                }}>
                  {o.status}
                </span>
              </td>
              <td style={{ padding: '0.6rem 1rem', color: '#6b7280' }}>
                {fmt.format(new Date(o.date))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
