import React from 'react'
import './Header.css'

function Header({ onReseed, backendStatus, onExport }) {
  const getStatusColor = () => {
    switch(backendStatus) {
      case 'connected': return '#4ecdc4'
      case 'disconnected': return '#ff6b6b'
      case 'error': return '#ffa500'
      default: return '#888'
    }
  }

  const getStatusText = () => {
    switch(backendStatus) {
      case 'connected': return 'Connected'
      case 'disconnected': return 'Disconnected'
      case 'error': return 'Error'
      default: return 'Checking...'
    }
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-section">
          <div className="logo">🔱</div>
          <div>
            <h1>TRISHUL</h1>
            <p className="subtitle">Threat Response Intelligence System</p>
          </div>
        </div>
        <div className="header-actions">
          <div className="status-indicator">
            <span className="status-dot" style={{background: getStatusColor()}}></span>
            <span className="status-text">{getStatusText()}</span>
          </div>
          <button className="export-btn" onClick={onExport}>
            📥 Export CSV
          </button>
          <button className="reseed-btn" onClick={onReseed}>
            🔄 Reseed Graph
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
