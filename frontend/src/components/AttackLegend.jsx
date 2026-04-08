import React from 'react'
import './AttackLegend.css'

function AttackLegend({ isAttacking, currentStep, currentNode, compromisedCount }) {
  return (
    <div className={`attack-legend ${isAttacking ? 'active' : ''}`}>
      <h3>🎯 Attack Visualization</h3>
      <div className="legend-items">
        <div className="legend-item">
          <span className="legend-indicator compromised"></span>
          <span>Compromised Node {compromisedCount > 0 && `(${compromisedCount})`}</span>
        </div>
        <div className="legend-item">
          <span className="legend-indicator attack-path"></span>
          <span>Attack Path</span>
        </div>
        <div className="legend-item">
          <span className="legend-indicator normal"></span>
          <span>Normal Node</span>
        </div>
      </div>
      {isAttacking && (
        <div className="attack-status">
          <div className="status-row">
            <span className="pulse-dot"></span>
            <span>Attack in Progress</span>
          </div>
          {currentStep !== undefined && (
            <div className="current-step">
              Step {currentStep} | At: {currentNode || 'Unknown'}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AttackLegend
