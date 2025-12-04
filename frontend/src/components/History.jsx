import './History.css'

function History({ history }) {
  // Handle empty state
  if (!history || history.length === 0) {
    return (
      <div className="history-container">
        <h2 className="history-title">Recent Visions</h2>
        <div className="empty-state">
          <p className="calm-message">✨ No visions have been revealed yet... ✨</p>
        </div>
      </div>
    )
  }

  return (
    <div className="history-container">
      <h2 className="history-title">Recent Visions</h2>
      <div className="history-list">
        {history.map((entry, index) => (
          <div key={index} className="history-entry">
            <div className="history-header">
              <span className={`history-score ${getScoreClass(entry.prediction_score)}`}>
                {entry.prediction_score}%
              </span>
              <span className="history-timestamp">
                {formatTimestamp(entry.timestamp)}
              </span>
            </div>
            <p className="history-message">{entry.mystical_message}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

// Helper function to determine score color class
function getScoreClass(score) {
  if (score >= 80) return 'green'
  if (score >= 60) return 'yellow'
  return 'red'
}

// Helper function to format timestamp
function formatTimestamp(timestamp) {
  if (!timestamp) return 'Unknown time'
  
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

export default History
