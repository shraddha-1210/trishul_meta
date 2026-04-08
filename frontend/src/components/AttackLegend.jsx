import React from 'react'
import { Crosshair } from 'lucide-react'
import './AttackLegend.css'

function AttackLegend({ isAttacking, currentStep, currentNode, compromisedCount }) {
  return (
    <div className={`attack-legend ${isAttacking ? 'active' : ''}`}>
      <div className="attack-legend-title">
        <Crosshair size={10} />
        Attack Visualization
      </div>
      <div className="legend-items">
        <div className="legend-item">
          <span className="legend-indicator compromised" />
          Compromised {compromisedCount > 0 && `(${compromisedCount})`}
        </div>
        <div className="legend-item">
          <span className="legend-indicator attack-path" />
          Attack Path
        </div>
        <div className="legend-item">
          <span className="legend-indicator normal" />
          Normal Node
        </div>
      </div>
      {isAttacking && (
        <div className="attack-status">
          <div className="status-row">
            <span className="pulse-dot" />
            Attack in Progress
          </div>
          {currentStep !== undefined && (
            <div className="current-step">
              Step {currentStep} · {currentNode || 'Unknown'}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AttackLegend
