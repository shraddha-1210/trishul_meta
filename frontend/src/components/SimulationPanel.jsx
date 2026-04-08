import React, { useEffect, useRef } from 'react'
import './SimulationPanel.css'

function SimulationPanel({ state, onStart, disabled }) {
  const logsEndRef = useRef(null)
  const [stepCount, setStepCount] = React.useState(0)

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    
    // Count steps from logs
    const steps = state.logs.filter(log => log.includes('Step ')).length
    setStepCount(steps)
  }, [state.logs])

  const handleClick = () => {
    console.log('Button clicked! Disabled:', disabled, 'Running:', state.running)
    if (!disabled && !state.running) {
      onStart()
    }
  }

  return (
    <div className="simulation-panel">
      <div className="simulation-header">
        <div>
          <h2>🤖 Live Simulation</h2>
          {state.running && (
            <div className="step-counter">
              Step {stepCount} | <span className="pulse">●</span> Running
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span style={{ 
            fontSize: '11px', 
            color: disabled ? '#ff6b6b' : '#4ecdc4',
            opacity: 0.7
          }}>
            {disabled ? '⚠️ Disabled' : '✅ Ready'}
          </span>
          <button 
            className="start-btn" 
            onClick={handleClick}
            disabled={disabled}
          >
            {state.running ? '⏳ Running...' : '▶️ Start Attack'}
          </button>
        </div>
      </div>

      <div className="simulation-logs">
        {state.logs.length === 0 ? (
          <div className="empty-state">
            <p>No simulation running</p>
            <p className="hint">Click "Start Attack" to begin</p>
          </div>
        ) : (
          <>
            {state.logs.map((log, idx) => {
              // Parse log to add styling
              const isStepLog = log.includes('Step ')
              const isSuccess = log.includes('crown_jewel_reached') || log.includes('Breached')
              const isBlocked = log.includes('blocked') || log.includes('Defended')
              const isStart = log.includes('initiated')
              const isEnd = log.includes('ended')
              
              let className = 'log-entry'
              if (isStepLog) className += ' log-step'
              if (isSuccess) className += ' log-success'
              if (isBlocked) className += ' log-blocked'
              if (isStart) className += ' log-start'
              if (isEnd) className += ' log-end'
              
              return (
                <div key={idx} className={className}>
                  {log}
                </div>
              )
            })}
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
