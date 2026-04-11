import { useState, useEffect, useCallback } from 'react'
import { fetchMessages } from '../api.js'

const INTENT_COLORS = {
  greeting:        '#a78bfa',
  product_inquiry: '#3b82f6',
  price_inquiry:   '#f59e0b',
  order_status:    '#25d366',
  unknown:         '#6b7a99',
}

const INTENT_LABELS = {
  greeting:        'Greeting',
  product_inquiry: 'Product Inquiry',
  price_inquiry:   'Price Inquiry',
  order_status:    'Order Status',
  unknown:         'Unknown',
}

function timeSince(dateStr) {
  const diff = (Date.now() - new Date(dateStr)) / 1000
  if (diff < 60) return `${Math.floor(diff)}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

export default function Overview() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchMessages(200)
      setData(res)
      setLastRefresh(new Date())
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  // Intent breakdown
  const intentCounts = {}
  const uniqueCustomers = new Set()
  if (data?.messages) {
    for (const m of data.messages) {
      const i = m.detected_intent || 'unknown'
      intentCounts[i] = (intentCounts[i] || 0) + 1
      if (m.customer_number) uniqueCustomers.add(m.customer_number)
    }
  }

  const totalMessages = data?.total ?? 0
  const maxCount = Math.max(...Object.values(intentCounts), 1)

  // Recent 5 messages
  const recent = data?.messages?.slice(0, 5) ?? []

  if (loading && !data) {
    return (
      <div className="loading">
        <div className="spinner" />
        Loading overview…
      </div>
    )
  }

  return (
    <>
      <div className="page-header">
        <h1>Overview</h1>
        <p>Real-time stats for your WhatsApp support bot</p>
        <div className="header-actions">
          <button className="refresh-btn" onClick={load}>
            ↻ Refresh
          </button>
          {lastRefresh && (
            <span style={{ fontSize: 11, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>
              Updated {timeSince(lastRefresh)}
            </span>
          )}
        </div>
      </div>

      <div className="page-content">
        {/* Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Messages</div>
            <div className="stat-value">{totalMessages}</div>
            <div className="stat-sub">All time</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Unique Customers</div>
            <div className="stat-value">{uniqueCustomers.size}</div>
            <div className="stat-sub">Distinct numbers</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Most Common Intent</div>
            <div className="stat-value" style={{ fontSize: 16, paddingTop: 6 }}>
              {Object.keys(intentCounts).length
                ? INTENT_LABELS[Object.entries(intentCounts).sort((a,b) => b[1]-a[1])[0][0]]
                : '—'}
            </div>
            <div className="stat-sub">By volume</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Intent Types</div>
            <div className="stat-value">{Object.keys(intentCounts).length}</div>
            <div className="stat-sub">Detected so far</div>
          </div>
        </div>

        <div className="two-col">
          {/* Intent breakdown */}
          <div className="card">
            <div className="card-title">Intent Breakdown</div>
            {Object.keys(intentCounts).length === 0 ? (
              <div className="empty">
                <div className="empty-icon">📭</div>
                No messages yet
              </div>
            ) : (
              <div className="intent-bars">
                {Object.entries(intentCounts)
                  .sort((a, b) => b[1] - a[1])
                  .map(([intent, count]) => (
                    <div key={intent} className="intent-row">
                      <span className="intent-row-label">{INTENT_LABELS[intent] ?? intent}</span>
                      <div className="intent-bar-wrap">
                        <div
                          className="intent-bar-fill"
                          style={{
                            width: `${(count / maxCount) * 100}%`,
                            background: INTENT_COLORS[intent] ?? '#6b7a99',
                          }}
                        />
                      </div>
                      <span className="intent-row-count">{count}</span>
                    </div>
                  ))}
              </div>
            )}
          </div>

          {/* Recent activity */}
          <div className="card">
            <div className="card-title">Recent Activity</div>
            {recent.length === 0 ? (
              <div className="empty">
                <div className="empty-icon">💤</div>
                No recent messages
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {recent.map(m => (
                  <div key={m.id} style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="mono" style={{ color: 'var(--muted)' }}>{m.customer_number}</span>
                      <span style={{ fontSize: 10, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>
                        {timeSince(m.timestamp)}
                      </span>
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text)' }}>{m.message_text}</div>
                    <div>
                      <span
                        className="badge"
                        style={{
                          background: `${INTENT_COLORS[m.detected_intent] ?? '#6b7a99'}18`,
                          color: INTENT_COLORS[m.detected_intent] ?? 'var(--muted)',
                          fontSize: 10,
                        }}
                      >
                        {m.detected_intent ?? 'unknown'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
