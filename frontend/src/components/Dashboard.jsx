import React, { useEffect, useState } from 'react'
import './Dashboard.css'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
    const interval = setInterval(loadDashboard, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const loadDashboard = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/dashboard')
      const data = await response.json()
      setStats(data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to load dashboard:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="dashboard loading">Loading dashboard...</div>
  }

  if (!stats || stats.error) {
    return <div className="dashboard error">Failed to load dashboard</div>
  }

  return (
    <div className="dashboard">
      <h2>📊 Dashboard</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_simulations || 0}</div>
          <div className="stat-label">Total Simulations</div>
        </div>
        
        <div className="stat-card danger">
          <div className="stat-value">{stats.breaches || 0}</div>
          <div className="stat-label">Breaches</div>
        </div>
        
        <div className="stat-card success">
          <div className="stat-value">{stats.blocked || 0}</div>
          <div className="stat-label">Blocked</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{stats.success_rate?.toFixed(1) || 0}%</div>
          <div className="stat-label">Attack Success Rate</div>
        </div>
      </div>

      {stats.current_graph && (
        <div className="graph-stats">
          <h3>Current Graph</h3>
          <div className="stats-row">
            <span>Nodes: {stats.current_graph.nodes}</span>
            <span>Edges: {stats.current_graph.edges}</span>
            <span>Entry Points: {stats.current_graph.entry_points}</span>
            <span>Crown Jewels: {stats.current_graph.crown_jewels}</span>
          </div>
        </div>
      )}

      {stats.top_targets && stats.top_targets.length > 0 && (
        <div className="top-targets">
          <h3>Most Targeted Services</h3>
          {stats.top_targets.map((target, idx) => (
            <div key={idx} className="target-item">
              <span className="target-name">{target.name}</span>
              <span className="target-count">{target.count} times</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Dashboard
