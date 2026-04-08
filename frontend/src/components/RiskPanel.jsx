import React from 'react'
import { Route, AlertOctagon, Lightbulb, Flame, Target, BarChart2 } from 'lucide-react'
import './RiskPanel.css'

function RiskPanel({ data, loading }) {
  if (loading) {
    return (
      <div className="risk-panel">
        <div className="panel-header">
          <AlertOctagon size={14} className="panel-header-icon" />
          <span className="panel-title">Risk Analysis</span>
        </div>
        <div className="loading-spinner">
          <div className="spinner" />
          <span>Loading risk data…</span>
        </div>
      </div>
    )
  }

  if (!data || (!data.attack_paths?.length && !data.riskiest_edges?.length)) {
    return (
      <div className="risk-panel">
        <div className="panel-header">
          <AlertOctagon size={14} className="panel-header-icon" />
          <span className="panel-title">Risk Analysis</span>
        </div>
        <p className="no-data">No risk data available</p>
      </div>
    )
  }

  const { riskiest_edges, attack_paths } = data

  return (
    <div className="risk-panel">
      {/* Attack Paths */}
      <div className="panel-header">
        <Route size={14} className="panel-header-icon" />
        <span className="panel-title">Attack Paths</span>
      </div>
      <div className="paths-list">
        {attack_paths.slice(0, 5).map((path, idx) => (
          <div key={idx} className="path-item">
            <div className="path-header">
              <span className="path-number">#{idx + 1}</span>
              <span className={`risk-badge ${getRiskLevel(path.total_risk)}`}>
                Risk {path.total_risk}
              </span>
            </div>
            <div className="path-route">{path.path.join(' → ')}</div>
            <div className="path-meta">
              <span><Target size={10} /> {path.crown_jewel}</span>
              <span><BarChart2 size={10} /> {(path.reach_probability * 100).toFixed(0)}% probability</span>
            </div>
          </div>
        ))}
      </div>

      <div className="section-divider" />

      {/* Riskiest Edges */}
      <div className="panel-header">
        <Flame size={14} className="panel-header-icon" />
        <span className="panel-title">Riskiest Edges</span>
      </div>
      <div className="edges-list">
        {riskiest_edges.slice(0, 6).map((edge, idx) => (
          <div key={idx} className="edge-item">
            <div className="edge-header">
              <span className="edge-route">{edge.src_name} → {edge.dst_name}</span>
              <span className={`risk-score ${getRiskLevel(edge.combined_risk)}`}>
                {edge.combined_risk}
              </span>
            </div>
            <div className="edge-type">{edge.edge_type}</div>
            <div className="edge-recommendation">
              <Lightbulb size={11} style={{ flexShrink: 0, marginTop: 1 }} />
              {edge.recommendation}
            </div>
            {edge.blast_radius > 0 && (
              <div className="blast-radius">
                <Flame size={10} />
                Blast radius: {edge.blast_radius} customers
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function getRiskLevel(risk) {
  if (risk > 0.7) return 'critical'
  if (risk > 0.5) return 'high'
  if (risk > 0.3) return 'medium'
  return 'low'
}

export default RiskPanel
