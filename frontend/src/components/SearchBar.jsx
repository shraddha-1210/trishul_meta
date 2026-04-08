import React, { useState } from 'react'
import './SearchBar.css'

function SearchBar({ onNodeSelect }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [showResults, setShowResults] = useState(false)

  const handleSearch = async (searchQuery) => {
    setQuery(searchQuery)
    
    if (searchQuery.length < 2) {
      setResults([])
      setShowResults(false)
      return
    }

    try {
      const response = await fetch(`http://localhost:8001/api/search?query=${encodeURIComponent(searchQuery)}`)
      const data = await response.json()
      setResults(data.results || [])
      setShowResults(true)
    } catch (error) {
      console.error('Search failed:', error)
    }
  }

  const selectNode = (node) => {
    setQuery(node.name)
    setShowResults(false)
    if (onNodeSelect) {
      onNodeSelect(node)
    }
  }

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="🔍 Search nodes..."
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        onFocus={() => results.length > 0 && setShowResults(true)}
      />
      
      {showResults && results.length > 0 && (
        <div className="search-results">
          {results.map((result, idx) => (
            <div
              key={idx}
              className="search-result-item"
              onClick={() => selectNode(result)}
            >
              <span className="result-name">{result.name}</span>
              <span className="result-type">{result.type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SearchBar
