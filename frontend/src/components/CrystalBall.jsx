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

  return (
    <div className="crystal-ball-container">
      <div className={`crystal-ball ${isGazing ? 'gazing' : ''}`}>
        <div className={`orb ${scoreColor}`}>
          <div className="mist"></div>
          <div className="score">
            {score !== null ? `${score}%` : '?'}
          </div>
        </div>
      </div>
      <div className="mystical-message">
        {message}
      </div>
    </div>
  )
}

export default CrystalBall
