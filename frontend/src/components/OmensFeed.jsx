import './OmensFeed.css'

function OmensFeed({ omens }) {
  // Icon mapping based on omen type
  const getOmenIcon = (type) => {
    switch (type) {
      case 'minor':
        return '⚠️'
      case 'major':
        return '🔥'
      case 'dark':
        return '☠️'
      default:
        return '⚠️'
    }
  }

  // Handle empty state
  if (!omens || omens.length === 0) {
    return (
      <div className="omens-feed">
        <h2 className="omens-title">Omens</h2>
        <div className="empty-state">
          <p className="calm-message">✨ The spirits see no disturbances... All is calm. ✨</p>
        </div>
      </div>
    )
  }

  return (
    <div className="omens-feed">
      <h2 className="omens-title">Omens</h2>
      <div className="omens-list">
        {omens.map((omen, index) => (
          <div key={index} className={`omen-card ${omen.type}`}>
            <div className="omen-header">
              <span className="omen-icon">{getOmenIcon(omen.type)}</span>
              <h3 className="omen-title">{omen.title}</h3>
              <span className={`severity-badge ${omen.type}`}>
                {omen.severity}/10
              </span>
            </div>
            <p className="omen-description">{omen.description}</p>
            <div className="omen-file">
              <span className="file-label">Affected file:</span>
              <code className="file-path">{omen.file}</code>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default OmensFeed
