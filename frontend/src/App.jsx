import { useState, useEffect } from 'react'
import './App.css'
import useWebSocket from './hooks/useWebSocket'
import CrystalBall from './components/CrystalBall'
import OmensFeed from './components/OmensFeed'
import History from './components/History'
import Recommendations from './components/Recommendations'
import EmojiExplosion from './components/EmojiExplosion'

function App() {
  // State management for predictions and history
  const [prediction, setPrediction] = useState(null)
  const [history, setHistory] = useState([])
  const [explosionTrigger, setExplosionTrigger] = useState(0)

  // WebSocket connection
  const { connected, lastMessage, reconnectAttempt } = useWebSocket('ws://207.180.199.169:8023/ws')

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      setPrediction(lastMessage)
      setExplosionTrigger(prev => prev + 1) // Trigger emoji explosion

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
      <EmojiExplosion trigger={explosionTrigger} score={prediction?.prediction_score} />
      <header className="app-header">
        <h1 className="mystical-title">
          <span className="emoji-icon">🔮</span>
          <span className="title-text">Crystal Ball CI/CD</span>
        </h1>
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
