import React, { useState, useEffect } from 'react'
import GraphView from './components/GraphView'
import RiskPanel from './components/RiskPanel'
import SimulationPanel from './components/SimulationPanel'
import Dashboard from './components/Dashboard'
import SearchBar from './components/SearchBar'
import Header from './components/Header'
import './App.css'

function App() {
  const [graphData, setGraphData] = useState(null)
  const [riskData, setRiskData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [simulationState, setSimulationState] = useState({
    running: false,
    logs: [],
    result: null
  })
  const [ws, setWs] = useState(null)
  const [backendStatus, setBackendStatus] = useState('checking')
  const [showExportMenu, setShowExportMenu] = useState(false)

  useEffect(() => {
    checkBackendHealth()
    loadGraph()
    loadRisk()
    
    // Connect WebSocket after a short delay to ensure backend is ready
    const wsTimeout = setTimeout(() => {
      connectWebSocket()
    }, 500)

    return () => {
      clearTimeout(wsTimeout)
      if (ws) ws.close()
    }
  }, [])

  const checkBackendHealth = async () => {
    console.log('🏥 Checking backend health...')
    try {
      const response = await fetch('http://localhost:8001/api/health')
      const data = await response.json()
      console.log('Backend health response:', data)
      
      if (data.status === 'ok') {
        setBackendStatus('connected')
        console.log('✅ Backend connected, nodes:', data.node_count)
        if (data.node_count === 0) {
          setError('Database is empty. Click "Reseed Graph" to populate.')
        }
      } else {
        setBackendStatus('error')
        setError(`Backend error: ${data.error}`)
      }
    } catch (err) {
      console.error('❌ Backend health check failed:', err)
      setBackendStatus('disconnected')
      setError('Cannot connect to backend. Make sure it\'s running on port 8001.')
    }
  }

  const connectWebSocket = () => {
    try {
      console.log('🔌 Connecting WebSocket to ws://localhost:8001/ws')
      const websocket = new WebSocket('ws://localhost:8001/ws')
      
      websocket.onopen = () => {
        console.log('✅ WebSocket connected')
        // Don't override backendStatus here, let health check handle it
      }
      
      websocket.onmessage = (event) => {
        console.log('📨 WebSocket message:', event.data)
        const data = JSON.parse(event.data)
        handleSimulationMessage(data)
      }

      websocket.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
      }
      
      websocket.onclose = () => {
        console.log('🔌 WebSocket closed, reconnecting in 3s...')
        setTimeout(connectWebSocket, 3000)
      }

      setWs(websocket)
    } catch (err) {
      console.error('Failed to connect WebSocket:', err)
      setTimeout(connectWebSocket, 3000)
    }
  }

  const handleSimulationMessage = (data) => {
    if (data.type === 'simulation_start') {
      setSimulationState({
        running: true,
        logs: [
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`,
          `🎯 ATTACK SIMULATION INITIATED`,
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`,
          `📍 Entry Point: ${data.entry}`,
          `⏰ Started at: ${new Date().toLocaleTimeString()}`,
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`,
          ``
        ],
        result: null
      })
      // Reset graph highlighting
      setGraphData(prev => ({
        ...prev,
        attackPath: [],
        compromisedNodes: []
      }))
    } else if (data.type === 'step') {
      setSimulationState(prev => ({
        ...prev,
        logs: [
          ...prev.logs,
          ``,
          `┌─ Step ${data.step + 1} ─────────────────────────────────`,
          `│ ${data.red_action}`,
          `│ ${data.blue_action}`,
          `│ Reward: ${data.reward > 0 ? '+' : ''}${data.reward.toFixed(1)}`,
          `└──────────────────────────────────────────`,
        ]
      }))
      
      // Update graph with attack visualization
      setGraphData(prev => ({
        ...prev,
        attackPath: data.attack_path || [],
        compromisedNodes: data.compromised_nodes || []
      }))
    } else if (data.type === 'simulation_end') {
      const isSuccess = data.result === 'crown_jewel_reached'
      setSimulationState(prev => ({
        ...prev,
        running: false,
        result: data.result,
        logs: [
          ...prev.logs,
          ``,
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`,
          `🏁 SIMULATION COMPLETE`,
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`,
          `Result: ${isSuccess ? '🚨 CROWN JEWEL BREACHED' : '🛡️ ATTACK BLOCKED'}`,
          `Attack Path: ${data.path.join(' → ')}`,
          `Total Steps: ${data.steps}`,
          `Duration: ${data.duration}s`,
          `⏰ Ended at: ${new Date().toLocaleTimeString()}`,
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`
        ]
      }))
      loadGraph()
      loadRisk()
    }
  }

  const loadGraph = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/graph')
      const data = await response.json()
      
      if (data.error) {
        setError(data.error)
      } else {
        setGraphData(data)
        setError(null)
      }
      setLoading(false)
    } catch (error) {
      console.error('Failed to load graph:', error)
      setError('Failed to load graph. Is backend running?')
      setLoading(false)
    }
  }

  const loadRisk = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/risk')
      const data = await response.json()
      
      if (!data.error) {
        setRiskData(data)
      }
    } catch (error) {
      console.error('Failed to load risk data:', error)
    }
  }

  const startSimulation = async () => {
    console.log('🎯 Start simulation clicked!')
    console.log('Backend status:', backendStatus)
    console.log('Simulation running:', simulationState.running)
    
    try {
      console.log('Sending POST to /api/simulate...')
      const response = await fetch('http://localhost:8001/api/simulate', { method: 'POST' })
      const result = await response.json()
      console.log('Simulation response:', result)
      
      if (result.status === 'error') {
        alert(result.message)
      } else {
        console.log('✅ Simulation started successfully')
      }
    } catch (error) {
      console.error('❌ Failed to start simulation:', error)
      alert('Failed to start simulation. Check that backend is running.')
    }
  }

  const reseedGraph = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8001/api/seed', { method: 'POST' })
      const result = await response.json()
      
      if (result.status === 'error') {
        alert(result.message)
      } else {
        await loadGraph()
        await loadRisk()
        setSimulationState({ running: false, logs: [], result: null })
        setError(null)
      }
    } catch (error) {
      console.error('Failed to reseed graph:', error)
      alert('Failed to reseed graph.')
    } finally {
      setLoading(false)
    }
  }

  const handleNodeSelect = async (node) => {
    try {
      const response = await fetch(`http://localhost:8001/api/node/${node.id}`)
      const data = await response.json()
      setSelectedNode(data)
    } catch (error) {
      console.error('Failed to load node details:', error)
    }
  }

  const exportToCSV = () => {
    window.open('http://localhost:8001/api/export/csv', '_blank')
  }

  return (
    <div className="app">
      <Header 
        onReseed={reseedGraph} 
        backendStatus={backendStatus}
        onExport={exportToCSV}
      />
      
      {/* Debug info */}
      <div style={{
        position: 'fixed',
        top: '70px',
        right: '10px',
        background: 'rgba(0,0,0,0.8)',
        color: '#fff',
        padding: '10px',
        borderRadius: '8px',
        fontSize: '11px',
        zIndex: 1000,
        fontFamily: 'monospace'
      }}>
        <div>Backend: <span style={{color: backendStatus === 'connected' ? '#4ecdc4' : '#ff6b6b'}}>{backendStatus}</span></div>
        <div>Simulation: {simulationState.running ? '🏃 Running' : '⏸️ Idle'}</div>
        <div>Logs: {simulationState.logs.length}</div>
        <div>WS: {ws ? (ws.readyState === 1 ? '✅ Open' : '❌ Closed') : '⚠️ None'}</div>
      </div>
      
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}
      
      <div className="main-content">
        <div className="left-panel">
          <SearchBar onNodeSelect={handleNodeSelect} />
          <GraphView 
            data={graphData} 
            loading={loading}
            selectedNode={selectedNode}
            onNodeClick={handleNodeSelect}
          />
        </div>
        <div className="right-panel">
          <Dashboard />
          <RiskPanel data={riskData} loading={loading} />
          <SimulationPanel 
            state={simulationState}
            onStart={startSimulation}
            disabled={simulationState.running || backendStatus !== 'connected'}
          />
        </div>
      </div>
      
      {selectedNode && (
        <div className="node-details-modal" onClick={() => setSelectedNode(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedNode(null)}>×</button>
            <h2>{selectedNode.node?.name}</h2>
            <div className="node-info">
              <p><strong>Type:</strong> {selectedNode.node?.type}</p>
              {selectedNode.node?.trust_score && (
                <p><strong>Trust Score:</strong> {selectedNode.node.trust_score}</p>
              )}
              {selectedNode.node?.anomaly_score && (
                <p><strong>Anomaly Score:</strong> {selectedNode.node.anomaly_score}</p>
              )}
            </div>
            {selectedNode.incoming?.length > 0 && (
              <div>
                <h3>Incoming Connections</h3>
                <ul>
                  {selectedNode.incoming.map((conn, idx) => (
                    <li key={idx}>{conn.source_name} → {conn.rel_type}</li>
                  ))}
                </ul>
              </div>
            )}
            {selectedNode.outgoing?.length > 0 && (
              <div>
                <h3>Outgoing Connections</h3>
                <ul>
                  {selectedNode.outgoing.map((conn, idx) => (
                    <li key={idx}>{conn.rel_type} → {conn.target_name}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
