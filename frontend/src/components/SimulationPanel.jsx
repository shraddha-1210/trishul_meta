import React, { useEffect, useRef } from 'react'
import './SimulationPanel.css'

function SimulationPanel({ state, onStart, disabled }) {
  const logsEndRef = useRef(null)

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [state.logs])

  return (
    <div className="simulation-panel">
      <div className="simulation-header">
        <h2>🤖 Live Simulation</h2>
        <button 
          className="start-btn" 
          onClick={onStart}
          disabled={disabled}
        >
          {state.running ? '⏳ Running...' : '▶️ Start Attack'}
        </button>
      </div>

      <div className="simulation-logs">
        {state.logs.length === 0 ? (
          <div className="empty-state">
            <p>No simulation running</p>
            <p className="hint">Click "Start Attack" to begin</p>
          </div>
        ) : (
          <>
            {state.logs.map((log, idx) => (
              <div key={idx} className="log-entry">
                {log}
              </div>
            ))}
            <div ref={logsEndRef} />
          </>
        )}
      </div>

      {state.result && (
        <div className={`simulation-result ${state.result}`}>
          {state.result === 'crown_jewel_reached' ? (
            <>
              <span className="result-icon">🚨</span>
              <span>Red Team Breached Crown Jewel!</span>
            </>
          ) : (
            <>
              <span className="result-icon">🛡️</span>
              <span>Blue Team Successfully Defended!</span>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default SimulationPanel
