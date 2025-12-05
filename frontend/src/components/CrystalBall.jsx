import { useState, useEffect } from 'react'
import './CrystalBall.css'

function CrystalBall({ prediction }) {
  const [isGazing, setIsGazing] = useState(false)

  // Trigger gazing animation when new prediction arrives
  useEffect(() => {
    if (prediction) {
      setIsGazing(true)
      const timer = setTimeout(() => setIsGazing(false), 2000)
      return () => clearTimeout(timer)
    }
  }, [prediction])

  // Determine color based on prediction score
  const getScoreColor = (score) => {
    if (score >= 80) return 'green'
    if (score >= 60) return 'yellow'
    return 'red'
  }

  const score = prediction?.prediction_score ?? null
  const message = prediction?.mystical_message ?? 'The spirits await...'
  const scoreColor = score !== null ? getScoreColor(score) : 'neutral'

  // Split long messages into multiple lines for curved text (pyramid shape)
  const splitMessage = (msg) => {
    const lineLimits = [40, 50, 60, 70, 80] // Pyramid: narrow->wide (5 lines)
    const words = msg.split(' ')
    const lines = []
    let currentLine = ''
    let lineIndex = 0

    words.forEach(word => {
      const testLine = currentLine ? `${currentLine} ${word}` : word

      if (testLine.length <= lineLimits[lineIndex]) {
        currentLine = testLine
      } else {
        if (currentLine) {
          lines.push(currentLine)
          lineIndex++
        }
        currentLine = word
        if (lineIndex >= lineLimits.length) return
      }
    })

    if (currentLine && lineIndex < lineLimits.length) {
      lines.push(currentLine)
    }

    return lines.slice(0, 5) // Max 5 lines
  }

  const messageLines = splitMessage(message)

  // Calculate font size based on message length
  const getFontSize = () => {
    const totalLength = message.length
    if (totalLength < 80) return 28
    if (totalLength < 120) return 24
    if (totalLength < 160) return 20
    return 18
  }

  const fontSize = getFontSize()

  return (
    <div className="crystal-ball-container">
      <div className={`crystal-ball ${isGazing ? 'gazing' : ''}`}>
        <div className={`orb ${scoreColor}`}>
          <div className="mist"></div>
          <div className="lightning"></div>
          <div className="lightning lightning-2"></div>
          {score === null ? (
            <div className="ghost">👻</div>
          ) : (
            <>
              <div className="flying-ghosts">
                <span className="flying-ghost fg-1">👻</span>
                <span className="flying-ghost fg-2">👻</span>
                <span className="flying-ghost fg-3">👻</span>
                <span className="flying-ghost fg-4">👻</span>
                <span className="flying-ghost fg-5">👻</span>
              </div>
              <div className="score">
                {score}%
              </div>
            </>
          )}
        </div>
      </div>
      <div className="mystical-message-box">
        <p className="mystical-message-text" style={{ fontSize: `${fontSize}px` }}>
          {message}
        </p>
      </div>
    </div>
  )
}

export default CrystalBall
