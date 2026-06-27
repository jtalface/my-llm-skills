import { useState } from 'preact/hooks'
import Dashboard from './components/Dashboard'
import DataTable from './components/DataTable'
import Charts from './components/Charts'
import Header from './components/Header'

// Native helpers replacing lodash
function sample(arr) { return arr[Math.floor(Math.random() * arr.length)] }
function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min }

// Sample data — generated at module load time (no lazy loading)
const SAMPLE_ORDERS = Array.from({ length: 500 }, () => ({
  id: crypto.randomUUID(),
  customer: sample(['Alice', 'Bob', 'Carol', 'Dave', 'Eve', 'Frank']),
  product: sample(['Widget A', 'Widget B', 'Gadget X', 'Gadget Y', 'Doohickey']),
  amount: randInt(10, 500),
  status: sample(['pending', 'shipped', 'delivered', 'cancelled']),
  date: new Date(Date.now() - randInt(0, 365) * 86400000).toISOString(),
  category: sample(['Electronics', 'Clothing', 'Books', 'Home', 'Sports']),
}))

export default function App() {
  const [orders] = useState(SAMPLE_ORDERS)
  const [filter, setFilter] = useState('all')
  const [sortKey, setSortKey] = useState('date')

  const filtered = orders
    .filter(o => filter === 'all' || o.status === filter)
    .sort((a, b) => (a[sortKey] < b[sortKey] ? -1 : a[sortKey] > b[sortKey] ? 1 : 0))

  const stats = {
    total: filtered.length,
    revenue: filtered.reduce((s, o) => s + o.amount, 0),
    avgOrder: filtered.length ? filtered.reduce((s, o) => s + o.amount, 0) / filtered.length : 0,
    byStatus: filtered.reduce((acc, o) => { acc[o.status] = (acc[o.status] || 0) + 1; return acc }, {}),
    byCategory: filtered.reduce((acc, o) => { (acc[o.category] = acc[o.category] || []).push(o); return acc }, {}),
  }

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '1rem' }}>
      <Header />
      <Dashboard stats={stats} />
      <Charts orders={filtered} />
      <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem' }}>
        {['all', 'pending', 'shipped', 'delivered', 'cancelled'].map(s => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            style={{
              padding: '0.4rem 0.8rem',
              background: filter === s ? '#3b82f6' : '#e5e7eb',
              color: filter === s ? '#fff' : '#222',
              border: 'none', borderRadius: 6, cursor: 'pointer',
            }}
          >
            {s}
          </button>
        ))}
      </div>
      <DataTable orders={filtered} onSort={setSortKey} sortKey={sortKey} />
    </div>
  )
}
