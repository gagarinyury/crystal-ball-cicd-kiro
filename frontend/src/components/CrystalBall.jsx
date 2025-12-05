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
      <div className="curved-text-container">
        <svg viewBox="0 0 300 50" className="curved-text-svg">
          <defs>
            <path id="curve" d="M 10,10 Q 150,60 290,10" fill="transparent" />
          </defs>
          <text className="curved-text">
            <textPath href="#curve" startOffset="50%" textAnchor="middle">
              {message.length > 60 ? message.slice(0, 60) + '...' : message}
            </textPath>
          </text>
        </svg>
      </div>
    </div>
  )
}

export default CrystalBall
