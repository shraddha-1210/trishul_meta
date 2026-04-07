import React, { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'
import cola from 'cytoscape-cola'
import './GraphView.css'

cytoscape.use(cola)

function GraphView({ data, loading }) {
  const containerRef = useRef(null)
  const cyRef = useRef(null)

  useEffect(() => {
    if (!data || !containerRef.current || !data.nodes || data.nodes.length === 0) return

    if (cyRef.current) {
      cyRef.current.destroy()
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements: [...data.nodes, ...data.edges],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele) => {
              const type = ele.data('type')
              if (type === 'Vendor') return ele.data('entry_point') ? '#ff6b6b' : '#4ecdc4'
              if (type === 'Service') return '#ffe66d'
              if (type === 'Pipeline') return '#a8dadc'
              if (type === 'Dependency') return '#f1a7fe'
              return '#95e1d3'
            },
            'label': 'data(name)',
            'color': '#fff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '10px',
            'font-weight': 'bold',
            'text-outline-width': 2,
            'text-outline-color': (ele) => {
              const type = ele.data('type')
              if (type === 'Vendor') return ele.data('entry_point') ? '#c92a2a' : '#0b7285'
              if (type === 'Service') return '#f59f00'
              if (type === 'Pipeline') return '#1864ab'
              if (type === 'Dependency') return '#9c36b5'
              return '#087f5b'
            },
            'width': (ele) => ele.data('crown_jewel') ? 60 : 40,
            'height': (ele) => ele.data('crown_jewel') ? 60 : 40,
            'border-width': (ele) => ele.data('crown_jewel') ? 4 : 2,
            'border-color': (ele) => ele.data('crown_jewel') ? '#ffd700' : 'rgba(255,255,255,0.3)',
            'border-style': (ele) => ele.data('crown_jewel') ? 'double' : 'solid'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': (ele) => {
              const anomaly = ele.data('anomaly') || 0
              if (anomaly > 0.8) return '#ff6b6b'
              if (anomaly > 0.5) return '#ffa500'
              return '#4ecdc4'
            },
            'target-arrow-color': (ele) => {
              const anomaly = ele.data('anomaly') || 0
              if (anomaly > 0.8) return '#ff6b6b'
              if (anomaly > 0.5) return '#ffa500'
              return '#4ecdc4'
            },
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'opacity': (ele) => ele.data('revoked') ? 0.3 : 0.8,
            'line-style': (ele) => ele.data('revoked') ? 'dashed' : 'solid'
          }
        }
      ],
      layout: {
        name: 'cola',
        animate: true,
        randomize: false,
        maxSimulationTime: 2000,
        nodeSpacing: 50,
        edgeLength: 100,
        fit: true,
        padding: 30
      }
    })

    cy.on('tap', 'node', (evt) => {
      const node = evt.target
      const data = node.data()
      console.log('Node clicked:', data)
    })

    cyRef.current = cy

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy()
      }
    }
  }, [data])

  return (
    <div className="graph-view">
      <div className="graph-header">
        <h2>Supply Chain Graph</h2>
        <div className="legend">
          <div className="legend-item">
            <span className="legend-dot" style={{background: '#ff6b6b'}}></span>
            Entry Point
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{background: '#ffe66d', border: '2px solid #ffd700'}}></span>
            Crown Jewel
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{background: '#4ecdc4'}}></span>
            Vendor
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{background: '#a8dadc'}}></span>
            Pipeline
          </div>
        </div>
      </div>
      <div ref={containerRef} className="graph-container">
        {loading && (
          <div className="graph-loading">
            <div className="spinner"></div>
            <p>Loading graph...</p>
          </div>
        )}
        {!loading && (!data || !data.nodes || data.nodes.length === 0) && (
          <div className="graph-empty">
            <p>No graph data available</p>
            <p className="hint">Click "Reseed Graph" to populate the database</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default GraphView
