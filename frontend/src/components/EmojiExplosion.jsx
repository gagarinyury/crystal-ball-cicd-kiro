import { useEffect, useState } from 'react'
import './EmojiExplosion.css'

const EMOJIS = ['🎃', '👻', '💀', '🦇', '🕷️', '🕸️', '🔮', '✨', '⭐', '🌙', '🪄', '🧙', '🧿', '👁️', '🌟', '💫', '🎭', '🦉', '🐈‍⬛', '🕯️']

function EmojiExplosion({ trigger, score }) {
  const [particles, setParticles] = useState([])

  useEffect(() => {
    if (trigger) {
      // Generate 30-50 random emoji particles
      const count = 30 + Math.floor(Math.random() * 20)
      const newParticles = []

      for (let i = 0; i < count; i++) {
        const emoji = EMOJIS[Math.floor(Math.random() * EMOJIS.length)]
        const side = Math.floor(Math.random() * 4) // 0: top, 1: right, 2: bottom, 3: left

        let startX, startY, endX, endY

        switch (side) {
          case 0: // from top
            startX = Math.random() * 100
            startY = -10
            endX = 30 + Math.random() * 40
            endY = 30 + Math.random() * 40
            break
          case 1: // from right
            startX = 110
            startY = Math.random() * 100
            endX = 30 + Math.random() * 40
            endY = 30 + Math.random() * 40
            break
          case 2: // from bottom
            startX = Math.random() * 100
            startY = 110
            endX = 30 + Math.random() * 40
            endY = 30 + Math.random() * 40
            break
          case 3: // from left
            startX = -10
            startY = Math.random() * 100
            endX = 30 + Math.random() * 40
            endY = 30 + Math.random() * 40
            break
        }

        newParticles.push({
          id: i,
          emoji,
          startX,
          startY,
          endX,
          endY,
          delay: Math.random() * 0.5,
          duration: 1 + Math.random() * 1,
          size: 1.5 + Math.random() * 2,
          rotation: Math.random() * 720 - 360
        })
      }

      setParticles(newParticles)

      // Clear particles after animation
      const timer = setTimeout(() => {
        setParticles([])
      }, 3000)

      return () => clearTimeout(timer)
    }
  }, [trigger])

  if (particles.length === 0) return null

  return (
    <div className="emoji-explosion">
      {particles.map((particle) => (
        <span
          key={particle.id}
          className="emoji-particle"
          style={{
            '--start-x': `${particle.startX}vw`,
            '--start-y': `${particle.startY}vh`,
            '--end-x': `${particle.endX}vw`,
            '--end-y': `${particle.endY}vh`,
            '--delay': `${particle.delay}s`,
            '--duration': `${particle.duration}s`,
            '--size': `${particle.size}rem`,
            '--rotation': `${particle.rotation}deg`
          }}
        >
          {particle.emoji}
        </span>
      ))}
    </div>
  )
}

export default EmojiExplosion
