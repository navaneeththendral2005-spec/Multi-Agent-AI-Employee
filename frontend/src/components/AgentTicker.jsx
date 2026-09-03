import { motion } from 'motion/react'
import { AGENT_TICKER_NAMES } from '../data/agents'

export default function AgentTicker() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.38, ease: 'easeOut' }}
      className="agent-ticker"
      aria-label="Available Chorus agents"
    >
      <div className="agent-ticker-track" aria-hidden="true">
        {[0, 1].map((group) => (
          <div key={group} className="agent-ticker-group">
            {AGENT_TICKER_NAMES.map((name, index) => (
              <span key={`${group}-${name}`} className="agent-ticker-item">
                <span className="agent-ticker-index">{String(index + 1).padStart(2, '0')}</span>
                {name}
              </span>
            ))}
          </div>
        ))}
      </div>
    </motion.div>
  )
}
