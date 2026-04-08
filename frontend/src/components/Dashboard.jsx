import React, { useEffect, useState } from 'react'
import { BarChart2, Zap, ShieldOff, ShieldCheck, TrendingUp, GitBranch, Target, Layers } from 'lucide-react'
import './Dashboard.css'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
    const interval = setInterval(loadDashboard, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadDashboard = async () => {
    try {
      const res = await fetch('http://localhost:8001/api/dashboard')
      setStats(await res.json())
      setLoading(false)
    } catch {
      setLoading(false)
    }
  }

  if (loading) return <div className="dashboard loading">Loading…</div>
  if (!stats || stats.error) return <div className="dashboard error">Failed to load dashboard</div>

  return (
    <div className="dashboard">
      <div className="panel-header">
        <BarChart2 size={14} className="panel-header-icon" />
        <span className="panel-title">Overview</span>
      </div>

      <div className="stats-grid">
        <div className="stat-card info">
          <div className="stat-value">{stats.total_simulations ?? 0}</div>
          <div className="stat-label">Simulations</div>
        </div>
        <div className="stat-card danger">
          <div className="stat-value">{stats.breaches ?? 0}</div>
          <div className="stat-label">Breaches</div>
        </div>
        <div className="stat-card success">
          <div className="stat-value">{stats.blocked ?? 0}</div>
          <div className="stat-label">Blocked</div>
        </div>
        <div className="stat-card warning">
          <div className="stat-value">{stats.success_rate?.toFixed(1) ?? 0}%</div>
          <div className="stat-label">Attack Rate</div>
        </div>
      </div>

      {stats.current_graph && (
        <div className="graph-stats">
          <div className="section-label">Current Graph</div>
          <div className="stats-row">
            <span><Layers size={11} /> {stats.current_graph.nodes} nodes</span>
            <span><GitBranch size={11} /> {stats.current_graph.edges} edges</span>
            <span><Zap size={11} /> {stats.current_graph.entry_points} entry</span>
            <span><Target size={11} /> {stats.current_graph.crown_jewels} jewels</span>
          </div>
        </div>
      )}

      {stats.top_targets?.length > 0 && (
        <div className="top-targets">
          <div className="section-label">Most Targeted</div>
          {stats.top_targets.map((t, i) => (
            <div key={i} className="target-item">
              <span className="target-name">{t.name}</span>
              <span className="target-count">{t.count}×</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Dashboard
