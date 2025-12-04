import { useState, useEffect } from 'react'
import './App.css'
import useWebSocket from './hooks/useWebSocket'
import CrystalBall from './components/CrystalBall'
import OmensFeed from './components/OmensFeed'
import History from './components/History'
import Recommendations from './components/Recommendations'

function App() {
  // State management for predictions and history
  const [prediction, setPrediction] = useState(null)
  const [history, setHistory] = useState([])
  
  // WebSocket connection
  const { connected, lastMessage, reconnectAttempt } = useWebSocket('ws://localhost:8000/ws')
  
  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      setPrediction(lastMessage)
      
      // Add to history with size constraint (max 10 items)
      setHistory(prevHistory => {
        const newHistory = [lastMessage, ...prevHistory]
        // Keep only the 10 most recent predictions
        return newHistory.slice(0, 10)
      })
    }
  }, [lastMessage])

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="mystical-title">🔮 Crystal Ball CI/CD</h1>
        <div className="connection-status">
          <span className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}>
            {connected ? '● Connected' : '○ Disconnected'}
          </span>
        </div>
      </header>

      <main className="app-main">
        <CrystalBall prediction={prediction} />
        <OmensFeed omens={prediction?.omens || []} />
        <Recommendations recommendations={prediction?.recommendations || []} />
        <History history={history} />
      </main>
    </div>
  )
}

export default App
