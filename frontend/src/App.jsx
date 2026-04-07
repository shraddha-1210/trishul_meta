import React, { useState, useEffect } from 'react'
import GraphView from './components/GraphView'
import RiskPanel from './components/RiskPanel'
import SimulationPanel from './components/SimulationPanel'
import Header from './components/Header'
import './App.css'

function App() {
  const [graphData, setGraphData] = useState(null)
  const [riskData, setRiskData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [simulationState, setSimulationState] = useState({
    running: false,
    logs: [],
    result: null
  })
  const [ws, setWs] = useState(null)
  const [backendStatus, setBackendStatus] = useState('checking')

  useEffect(() => {
    checkBackendHealth()
    loadGraph()
    loadRisk()
    connectWebSocket()

    return () => {
      if (ws) ws.close()
    }
  }, [])

  const checkBackendHealth = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/health')
      const data = await response.json()
      
      if (data.status === 'ok') {
        setBackendStatus('connected')
        if (data.node_count === 0) {
          setError('Database is empty. Click "Reseed Graph" to populate.')
        }
      } else {
        setBackendStatus('error')
        setError(`Backend error: ${data.error}`)
      }
    } catch (err) {
      setBackendStatus('disconnected')
      setError('Cannot connect to backend. Make sure it\'s running on port 8001.')
    }
  }

  const connectWebSocket = () => {
    try {
      const websocket = new WebSocket('ws://localhost:8001/ws')
      
      websocket.onopen = () => {
        console.log('✅ WebSocket connected')
      }
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        handleSimulationMessage(data)
      }

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
      
      websocket.onclose = () => {
        console.log('WebSocket closed')
      }

      setWs(websocket)
    } catch (err) {
      console.error('Failed to connect WebSocket:', err)
    }
  }

  const handleSimulationMessage = (data) => {
    if (data.type === 'simulation_start') {
      setSimulationState({
        running: true,
        logs: [`🎯 Attack initiated from: ${data.entry}`],
        result: null
      })
    } else if (data.type === 'step') {
      setSimulationState(prev => ({
        ...prev,
        logs: [
          ...prev.logs,
          `Step ${data.step}: Red at ${data.red_position} | ${data.red_action} | Blue: ${data.blue_action}`
        ]
      }))
    } else if (data.type === 'simulation_end') {
      setSimulationState(prev => ({
        ...prev,
        running: false,
        result: data.result,
        logs: [
          ...prev.logs,
          `\n🏁 Simulation ended: ${data.result}`,
          `Attack path: ${data.path.join(' → ')}`
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
    try {
      const response = await fetch('http://localhost:8001/api/simulate', { method: 'POST' })
      const result = await response.json()
      
      if (result.status === 'error') {
        alert(result.message)
      }
    } catch (error) {
      console.error('Failed to start simulation:', error)
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

  return (
    <div className="app">
      <Header onReseed={reseedGraph} backendStatus={backendStatus} />
      
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}
      
      <div className="main-content">
        <div className="left-panel">
          <GraphView data={graphData} loading={loading} />
        </div>
        <div className="right-panel">
          <RiskPanel data={riskData} loading={loading} />
          <SimulationPanel 
            state={simulationState}
            onStart={startSimulation}
            disabled={simulationState.running || backendStatus !== 'connected'}
          />
        </div>
      </div>
    </div>
  )
}

export default App
