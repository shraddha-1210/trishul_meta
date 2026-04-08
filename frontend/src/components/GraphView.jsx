import React, { useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import cola from 'cytoscape-cola'
import AttackLegend from './AttackLegend'
import { Network } from 'lucide-react'
import './GraphView.css'

cytoscape.use(cola)

function GraphView({ data, loading, selectedNode, onNodeClick }) {
  const containerRef = useRef(null)
  const cyRef = useRef(null)
  const [attackPath, setAttackPath] = useState([])
  const [compromisedNodes, setCompromisedNodes] = useState([])
  const [currentStep, setCurrentStep] = useState(0)
  const [currentNode, setCurrentNode] = useState('')

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
              const nodeId = ele.data('id')
              const type = ele.data('type')
              
              // Highlight compromised nodes
              if (compromisedNodes.includes(nodeId)) {
                return '#ff0000'
              }
              
              // Highlight current attack path
              if (attackPath.includes(nodeId)) {
                return '#ff6b6b'
              }
              
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
              const nodeId = ele.data('id')
              if (compromisedNodes.includes(nodeId)) return '#8b0000'
              if (attackPath.includes(nodeId)) return '#c92a2a'
              
              const type = ele.data('type')
              if (type === 'Vendor') return ele.data('entry_point') ? '#c92a2a' : '#0b7285'
              if (type === 'Service') return '#f59f00'
              if (type === 'Pipeline') return '#1864ab'
              if (type === 'Dependency') return '#9c36b5'
              return '#087f5b'
            },
            'width': (ele) => {
              if (compromisedNodes.includes(ele.data('id'))) return 70
              return ele.data('crown_jewel') ? 60 : 40
            },
            'height': (ele) => {
              if (compromisedNodes.includes(ele.data('id'))) return 70
              return ele.data('crown_jewel') ? 60 : 40
            },
            'border-width': (ele) => {
              if (compromisedNodes.includes(ele.data('id'))) return 5
              return ele.data('crown_jewel') ? 4 : 2
            },
            'border-color': (ele) => {
              if (compromisedNodes.includes(ele.data('id'))) return '#ff0000'
              return ele.data('crown_jewel') ? '#ffd700' : 'rgba(255,255,255,0.3)'
            },
            'border-style': (ele) => {
              if (compromisedNodes.includes(ele.data('id'))) return 'solid'
              return ele.data('crown_jewel') ? 'double' : 'solid'
            },
            'transition-property': 'background-color, border-color, width, height',
            'transition-duration': '0.5s'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': (ele) => {
              // Highlight edges in attack path
              const source = ele.data('source')
              const target = ele.data('target')
              const sourceInPath = attackPath.includes(source)
              const targetInPath = attackPath.includes(target)
              if (sourceInPath && targetInPath) return 4
              return 2
            },
            'line-color': (ele) => {
              const source = ele.data('source')
              const target = ele.data('target')
              const sourceInPath = attackPath.includes(source)
              const targetInPath = attackPath.includes(target)
              
              if (sourceInPath && targetInPath) return '#ff0000'
              
              const anomaly = ele.data('anomaly') || 0
              if (anomaly > 0.8) return '#ff6b6b'
              if (anomaly > 0.5) return '#ffa500'
              return '#4ecdc4'
            },
            'target-arrow-color': (ele) => {
              const source = ele.data('source')
              const target = ele.data('target')
              const sourceInPath = attackPath.includes(source)
              const targetInPath = attackPath.includes(target)
              
              if (sourceInPath && targetInPath) return '#ff0000'
              
              const anomaly = ele.data('anomaly') || 0
              if (anomaly > 0.8) return '#ff6b6b'
              if (anomaly > 0.5) return '#ffa500'
              return '#4ecdc4'
            },
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'opacity': (ele) => {
              const source = ele.data('source')
              const target = ele.data('target')
              const sourceInPath = attackPath.includes(source)
              const targetInPath = attackPath.includes(target)
              
              if (sourceInPath && targetInPath) return 1
              if (ele.data('revoked')) return 0.3
              return 0.8
            },
            'line-style': (ele) => ele.data('revoked') ? 'dashed' : 'solid',
            'transition-property': 'line-color, width, opacity',
            'transition-duration': '0.5s'
          }
        },
        {
          selector: 'node.highlighted',
          style: {
            'border-width': 6,
            'border-color': '#ff0000',
            'background-color': '#ff6b6b'
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
      if (onNodeClick) {
        onNodeClick(data)
      }
    })

    cyRef.current = cy

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy()
      }
    }
  }, [data, attackPath, compromisedNodes])

  // Listen for attack updates via props
  useEffect(() => {
    if (data?.attackPath) {
      setAttackPath(data.attackPath)
      // Update current node (last in path)
      if (data.attackPath.length > 0) {
        setCurrentNode(data.attackPath[data.attackPath.length - 1])
        setCurrentStep(data.attackPath.length)
      }
    }
    if (data?.compromisedNodes) {
      setCompromisedNodes(data.compromisedNodes)
    }
  }, [data])

  return (
    <div className="graph-view">
      <div className="graph-header">
        <div className="graph-title-row">
          <Network size={14} style={{ color: 'var(--text-muted)' }} />
          <span className="graph-title">Supply Chain Graph</span>
        </div>
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
        <AttackLegend 
          isAttacking={compromisedNodes.length > 0}
          currentStep={currentStep}
          currentNode={currentNode}
          compromisedCount={compromisedNodes.length}
        />
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
