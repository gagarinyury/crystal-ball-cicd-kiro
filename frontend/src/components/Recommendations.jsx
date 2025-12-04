import './Recommendations.css'

function Recommendations({ recommendations }) {
  // Don't render if no recommendations
  if (!recommendations || recommendations.length === 0) {
    return null
  }

  return (
    <div className="recommendations-container">
      <h2 className="recommendations-title">✨ Mystical Guidance ✨</h2>
      <div className="recommendations-list">
        {recommendations.map((recommendation, index) => (
          <div key={index} className="recommendation-item">
            <span className="recommendation-icon">🔮</span>
            <p className="recommendation-text">{recommendation}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Recommendations
