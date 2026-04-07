import React from 'react'
import './RiskPanel.css'

function RiskPanel({ data, loading }) {
  if (loading) {
    return (
      <div className="risk-panel">
        <h2>Risk Analysis</h2>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading risk data...</p>
        </div>
      </div>
    )
  }

  if (!data || (!data.attack_paths?.length && !data.riskiest_edges?.length)) {
    return (
      <div className="risk-panel">
        <h2>Risk Analysis</h2>
        <p className="no-data">No risk data available</p>
      </div>
    )
  }

  const { riskiest_edges, attack_paths } = data

  return (
    <div className="risk-panel">
      <h2>🎯 Attack Paths</h2>
      <div className="paths-list">
        {attack_paths.slice(0, 5).map((path, idx) => (
          <div key={idx} className="path-item">
            <div className="path-header">
              <span className="path-number">#{idx + 1}</span>
              <span className={`risk-badge ${getRiskLevel(path.total_risk)}`}>
                Risk: {path.total_risk}
              </span>
            </div>
            <div className="path-route">
              {path.path.join(' → ')}
            </div>
            <div className="path-meta">
              <span>🎯 {path.crown_jewel}</span>
              <span>📊 {(path.reach_probability * 100).toFixed(0)}% probability</span>
            </div>
          </div>
        ))}
      </div>

      <h2>⚠️ Riskiest Edges</h2>
      <div className="edges-list">
        {riskiest_edges.slice(0, 8).map((edge, idx) => (
          <div key={idx} className="edge-item">
            <div className="edge-header">
              <span className="edge-route">
                {edge.src_name} → {edge.dst_name}
              </span>
              <span className={`risk-score ${getRiskLevel(edge.combined_risk)}`}>
                {edge.combined_risk}
              </span>
            </div>
            <div className="edge-type">{edge.edge_type}</div>
            <div className="edge-recommendation">
              💡 {edge.recommendation}
            </div>
            {edge.blast_radius > 0 && (
              <div className="blast-radius">
                💥 Blast radius: {edge.blast_radius} customers
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
