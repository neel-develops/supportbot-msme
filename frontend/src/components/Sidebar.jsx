import { useState, useEffect } from 'react'
import { fetchHealth } from '../api.js'

const NAV = [
  { id: 'overview',      icon: '◈', label: 'Overview' },
  { id: 'conversations', icon: '💬', label: 'Conversations' },
  { id: 'products',      icon: '📦', label: 'Products' },
  { id: 'testbot',       icon: '⚡', label: 'Test Bot' },
]

export default function Sidebar({ active, setActive }) {
  const [healthy, setHealthy] = useState(null)

  useEffect(() => {
    fetchHealth()
      .then(() => setHealthy(true))
      .catch(() => setHealthy(false))
  }, [])

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🤖</div>
        <div className="sidebar-logo-text">
          SupportBot
          <span>MSME Dashboard</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV.map(item => (
          <button
            key={item.id}
            className={`nav-item${active === item.id ? ' active' : ''}`}
            onClick={() => setActive(item.id)}
          >
            <span className="nav-item-icon">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-badge">
          <div className={`status-dot${healthy === false ? ' offline' : ''}`} />
          {healthy === null ? 'Checking…' : healthy ? 'API online' : 'API offline'}
        </div>
      </div>
    </aside>
  )
}
