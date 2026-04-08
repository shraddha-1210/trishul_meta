import React, { useEffect, useState } from 'react'
import { ShieldAlert, Download, RefreshCw, Sun, Moon, Wifi, WifiOff, AlertTriangle } from 'lucide-react'
import './Header.css'

function Header({ onReseed, backendStatus, onExport }) {
  const [theme, setTheme] = useState(() => localStorage.getItem('trishul-theme') || 'dark')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('trishul-theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark')

  const statusConfig = {
    connected:    { color: '#22c55e', label: 'Connected',    Icon: Wifi,          pulse: true  },
    disconnected: { color: '#ef4444', label: 'Disconnected', Icon: WifiOff,       pulse: false },
    error:        { color: '#f59e0b', label: 'Error',        Icon: AlertTriangle, pulse: false },
    checking:     { color: '#6b7280', label: 'Checking…',    Icon: Wifi,          pulse: true  },
  }

  const { color, label, Icon, pulse } = statusConfig[backendStatus] || statusConfig.checking

  return (
    <header className="header">
      <div className="header-content">
        {/* Logo */}
        <div className="logo-section">
          <div className="logo-icon">
            <ShieldAlert size={18} strokeWidth={2.2} />
          </div>
          <div className="logo-text">
            <h1>TRISHUL</h1>
            <p className="subtitle">Threat Response Intelligence System</p>
          </div>
        </div>

        {/* Actions */}
        <div className="header-actions">
          {/* Status */}
          <div className="status-indicator">
            <span className={`status-dot ${pulse ? 'pulse' : ''}`} style={{ background: color }} />
            <Icon size={11} style={{ color }} />
            <span className="status-text">{label}</span>
          </div>

          <div className="header-divider" />

          <button className="header-btn" onClick={onExport} title="Export CSV">
            <Download size={13} />
            Export CSV
          </button>

          <button className="header-btn primary" onClick={onReseed} title="Reseed Graph">
            <RefreshCw size={13} />
            Reseed Graph
          </button>

          <div className="header-divider" />

          <button className="theme-toggle" onClick={toggleTheme} title="Toggle theme">
            {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
