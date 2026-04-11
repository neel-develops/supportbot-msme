import { useState, useEffect, useCallback } from 'react'
import { fetchMessages } from '../api.js'

const INTENT_CLASS = {
  greeting:        'badge-blue',
  product_inquiry: 'badge-blue',
  price_inquiry:   'badge-yellow',
  order_status:    'badge-green',
  unknown:         'badge-gray',
}

function formatDate(str) {
  if (!str) return '—'
  const d = new Date(str)
  return d.toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

export default function Conversations() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [limit, setLimit] = useState(50)
  const [filter, setFilter] = useState('')
  const [intentFilter, setIntentFilter] = useState('all')
  const [expanded, setExpanded] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchMessages(limit)
      setData(res)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [limit])

  useEffect(() => { load() }, [load])

  const messages = data?.messages ?? []

  const allIntents = [...new Set(messages.map(m => m.detected_intent).filter(Boolean))]

  const filtered = messages.filter(m => {
    const matchText =
      !filter ||
      m.message_text?.toLowerCase().includes(filter.toLowerCase()) ||
      m.customer_number?.includes(filter)
    const matchIntent =
      intentFilter === 'all' || m.detected_intent === intentFilter
    return matchText && matchIntent
  })

  return (
    <>
      <div className="page-header">
        <h1>Conversations</h1>
        <p>Full message log with intent labels and bot replies</p>
        <div className="header-actions">
          <button className="refresh-btn" onClick={load}>↻ Refresh</button>
          <select
            value={limit}
            onChange={e => setLimit(Number(e.target.value))}
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              color: 'var(--muted)',
              borderRadius: 6,
              padding: '5px 10px',
              fontSize: 12,
              fontFamily: 'var(--font)',
              cursor: 'pointer',
            }}
          >
            <option value={25}>25 rows</option>
            <option value={50}>50 rows</option>
            <option value={100}>100 rows</option>
            <option value={200}>200 rows</option>
          </select>
        </div>
      </div>

      <div className="page-content">
        {/* Filters */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
          <input
            placeholder="Search number or message…"
            value={filter}
            onChange={e => setFilter(e.target.value)}
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 7,
              padding: '8px 13px',
              color: 'var(--text)',
              fontSize: 13,
              fontFamily: 'var(--font)',
              width: 240,
              outline: 'none',
            }}
          />
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {['all', ...allIntents].map(i => (
              <button
                key={i}
                className={`badge ${intentFilter === i ? 'badge-green' : 'badge-gray'}`}
                style={{ cursor: 'pointer', border: 'none' }}
                onClick={() => setIntentFilter(i)}
              >
                {i}
              </button>
            ))}
          </div>
        </div>

        <div className="card" style={{ padding: 0 }}>
          {loading && !data ? (
            <div className="loading"><div className="spinner" />Loading…</div>
          ) : filtered.length === 0 ? (
            <div className="empty">
              <div className="empty-icon">💬</div>
              No messages found
            </div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Customer</th>
                    <th>Message</th>
                    <th>Intent</th>
                    <th>Timestamp</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(m => (
                    <>
                      <tr key={m.id}>
                        <td className="mono" style={{ color: 'var(--muted)' }}>{m.id}</td>
                        <td className="mono">{m.customer_number}</td>
                        <td style={{ maxWidth: 280 }}>
                          <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 260 }}>
                            {m.message_text}
                          </div>
                        </td>
                        <td>
                          <span className={`badge ${INTENT_CLASS[m.detected_intent] ?? 'badge-gray'}`}>
                            {m.detected_intent ?? 'unknown'}
                          </span>
                        </td>
                        <td className="mono" style={{ fontSize: 11, color: 'var(--muted)', whiteSpace: 'nowrap' }}>
                          {formatDate(m.timestamp)}
                        </td>
                        <td>
                          <button
                            className="btn btn-ghost"
                            style={{ padding: '4px 10px', fontSize: 11 }}
                            onClick={() => setExpanded(expanded === m.id ? null : m.id)}
                          >
                            {expanded === m.id ? '▲ Hide' : '▼ Reply'}
                          </button>
                        </td>
                      </tr>
                      {expanded === m.id && (
                        <tr key={`${m.id}-reply`}>
                          <td />
                          <td colSpan={5} style={{ paddingBottom: 14 }}>
                            <div style={{
                              background: 'var(--bg)',
                              border: '1px solid var(--border)',
                              borderRadius: 7,
                              padding: '12px 14px',
                              fontSize: 12,
                              color: 'var(--muted)',
                              lineHeight: 1.6,
                            }}>
                              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--muted)', display: 'block', marginBottom: 4 }}>
                                🤖 BOT REPLY
                              </span>
                              {m.bot_reply ?? 'No reply recorded.'}
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div style={{ marginTop: 10, fontSize: 11, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>
          Showing {filtered.length} of {data?.total ?? 0} total messages
        </div>
      </div>
    </>
  )
}
