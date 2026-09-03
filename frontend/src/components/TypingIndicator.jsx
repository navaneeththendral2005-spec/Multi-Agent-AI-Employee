import { motion } from 'motion/react'
import { AGENTS } from '../data/agents'

export default function TypingIndicator({ agentId }) {
  const agent = AGENTS.find((a) => a.id === agentId)
  if (!agent) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="flex items-center gap-2 text-ink-soft"
    >
      <span className="h-2 w-2 rounded-full" style={{ background: agent.color }} />
      <span className="text-xs font-semibold" style={{ color: agent.color }}>
        {agent.name}
      </span>
      <span className="flex items-center gap-0.5 pl-0.5">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-ink-faint"
            animate={{ y: [0, -3, 0] }}
            transition={{ duration: 0.9, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
          />
        ))}
      </span>
    </motion.div>
  )
}
