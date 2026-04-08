import React, { useEffect, useRef, useState } from 'react'
import { Play, Loader2, ShieldCheck, ShieldOff, Terminal } from 'lucide-react'
import './SimulationPanel.css'

function SimulationPanel({ state, onStart, disabled }) {
  const logsEndRef = useRef(null)
  const [stepCount, setStepCount] = useState(0)

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    setStepCount(state.logs.filter(l => l.includes('Step ')).length)
  }, [state.logs])

  return (
    <div className="simulation-panel">
      <div className="simulation-header">
        <div className="sim-title-row">
          <div className="panel-header" style={{ marginBottom: 0, paddingBottom: 0, border: 'none' }}>
            <Terminal size={14} className="panel-header-icon" />
            <span className="panel-title">Live Simulation</span>
          </div>
          {state.running && (
            <div className="step-counter">
              <span className="live-dot" />
              Step {stepCount} · Running
            </div>
          )}
        </div>

        <div className="sim-controls">
          <div className={`sim-status-badge ${disabled ? 'error' : 'ready'}`}>
            {disabled
              ? <><ShieldOff size={10} /> Disabled</>
              : <><ShieldCheck size={10} /> Ready</>
            }
          </div>
          <button
            className="start-btn"
            onClick={() => !disabled && !state.running && onStart()}
            disabled={disabled || state.running}
          >
            {state.running
              ? <><Loader2 size={12} style={{ animation: 'spin 1s linear infinite' }} /> Running…</>
              : <><Play size={12} /> Start Attack</>
            }
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
              let cls = 'log-entry'
              if (log.includes('Step '))                                          cls += ' log-step'
              if (log.includes('crown_jewel_reached') || log.includes('Breached')) cls += ' log-success'
              if (log.includes('blocked') || log.includes('Defended'))            cls += ' log-blocked'
              if (log.includes('initiated'))                                       cls += ' log-start'
              if (log.includes('ended') || log.includes('COMPLETE'))              cls += ' log-end'
              return <div key={idx} className={cls}>{log}</div>
            })}
            <div ref={logsEndRef} />
          </>
        )}
      </div>

      {state.result && (
        <div className={`simulation-result ${state.result}`}>
          {state.result === 'crown_jewel_reached'
            ? <><ShieldOff size={14} /> Red Team Breached Crown Jewel</>
            : <><ShieldCheck size={14} /> Blue Team Successfully Defended</>
          }
        </div>
      )}
    </div>
  )
}

export default SimulationPanel
