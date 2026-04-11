import { useState, useRef, useEffect } from 'react'
import { simulateMessage } from '../api.js'

const QUICK_MSGS = [
  'Do you have laptop bags?',
  'What is the price of USB hub?',
  'Where is my order ORD-1001?',
  'Hello!',
  'Do you have wireless earphones in stock?',
  'How much does the phone stand cost?',
]

const INTENT_LABEL = {
  greeting:        '👋 Greeting',
  product_inquiry: '🔍 Product Inquiry',
  price_inquiry:   '💰 Price Inquiry',
  order_status:    '📦 Order Status',
  unknown:         '❓ Unknown',
}

export default function TestBot() {
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hi! I\'m the SupportBot simulator. Send me a test message to see how I respond.', meta: null }
  ])
  const [input, setInput] = useState('')
  const [phone, setPhone] = useState('919999999999')
  const [loading, setLoading] = useState(false)
  const [lastResult, setLastResult] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const msg = text ?? input.trim()
    if (!msg || loading) return
    setInput('')

    setMessages(prev => [...prev, { role: 'user', text: msg, meta: null }])
    setLoading(true)

    try {
      const result = await simulateMessage(phone, msg)
      setLastResult(result)
      setMessages(prev => [
        ...prev,
        {
          role: 'bot',
          text: result.reply ?? 'No reply.',
          meta: result.intent,
        }
      ])
    } catch (e) {
      setMessages(prev => [
        ...prev,
        { role: 'bot', text: '⚠️ Could not reach the API. Is the backend running?', meta: null }
      ])
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([{ role: 'bot', text: 'Chat cleared. Send a new message!', meta: null }])
    setLastResult(null)
  }

  return (
    <>
      <div className="page-header">
        <h1>Test Bot</h1>
        <p>Send test messages to the AI pipeline without WhatsApp</p>
      </div>

      <div className="page-content">
        {/* Phone config */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 16, alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ fontSize: 12, color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: 8 }}>
            📱 Simulated phone:
            <input
              value={phone}
              onChange={e => setPhone(e.target.value)}
              style={{
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                padding: '5px 10px',
                color: 'var(--text)',
                fontFamily: 'var(--mono)',
                fontSize: 12,
                width: 160,
                outline: 'none',
              }}
            />
          </label>
          <button className="btn btn-ghost" style={{ fontSize: 12, padding: '5px 12px' }} onClick={clearChat}>
            Clear chat
          </button>
        </div>

        {/* Quick prompts */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 14 }}>
          {QUICK_MSGS.map(q => (
            <button
              key={q}
              className="badge badge-gray"
              style={{ cursor: 'pointer', border: 'none', fontSize: 11, padding: '4px 10px' }}
              onClick={() => send(q)}
              disabled={loading}
            >
              {q}
            </button>
          ))}
        </div>

        <div className="testbot-wrap">
          {/* Chat window */}
          <div className="chat-window">
            <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--accent)', boxShadow: '0 0 6px var(--accent)' }} />
              <span style={{ fontSize: 12, fontWeight: 600 }}>WhatsApp Simulator</span>
              <span className="mono" style={{ fontSize: 10, color: 'var(--muted)', marginLeft: 'auto' }}>+{phone}</span>
            </div>

            <div className="chat-messages">
              {messages.map((m, i) => (
                <div key={i} className={`chat-bubble ${m.role}`}>
                  {m.text}
                  {m.meta && (
                    <div className="meta">
                      {INTENT_LABEL[m.meta] ?? m.meta}
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="chat-bubble bot" style={{ opacity: 0.6 }}>
                  <div className="spinner" style={{ width: 12, height: 12, display: 'inline-block' }} /> Thinking…
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            <div className="chat-input-row">
              <input
                placeholder="Type a customer message…"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && send()}
                disabled={loading}
              />
              <button
                className="btn btn-primary"
                onClick={() => send()}
                disabled={loading || !input.trim()}
              >
                Send
              </button>
            </div>
          </div>

          {/* Debug panel */}
          <div className="debug-panel">
            <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 11, fontWeight: 600, fontFamily: 'var(--mono)', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                API Response Debug
              </span>
            </div>
            <pre>
              {lastResult
                ? JSON.stringify(lastResult, null, 2)
                : '// Response will appear here after you send a message\n\n// Example response:\n// {\n//   "status": "ok",\n//   "intent": "product_inquiry",\n//   "reply": "Yes, we have Laptop Bags..."\n// }'}
            </pre>
          </div>
        </div>
      </div>
    </>
  )
}
