import React, { useState } from 'react'
import { Search } from 'lucide-react'
import './SearchBar.css'

function SearchBar({ onNodeSelect }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [showResults, setShowResults] = useState(false)

  const handleSearch = async (q) => {
    setQuery(q)
    if (q.length < 2) { setResults([]); setShowResults(false); return }
    try {
      const res = await fetch(`http://localhost:8001/api/search?query=${encodeURIComponent(q)}`)
      const data = await res.json()
      setResults(data.results || [])
      setShowResults(true)
    } catch { /* silent */ }
  }

  const selectNode = (node) => {
    setQuery(node.name)
    setShowResults(false)
    onNodeSelect?.(node)
  }

  return (
    <div className="search-bar">
      <div className="search-input-wrap">
        <Search size={13} className="search-icon" />
        <input
          type="text"
          placeholder="Search nodes…"
          value={query}
          onChange={e => handleSearch(e.target.value)}
          onFocus={() => results.length > 0 && setShowResults(true)}
          onBlur={() => setTimeout(() => setShowResults(false), 150)}
        />
      </div>
      {showResults && results.length > 0 && (
        <div className="search-results">
          {results.map((r, i) => (
            <div key={i} className="search-result-item" onMouseDown={() => selectNode(r)}>
              <span className="result-name">{r.name}</span>
              <span className="result-type">{r.type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SearchBar
