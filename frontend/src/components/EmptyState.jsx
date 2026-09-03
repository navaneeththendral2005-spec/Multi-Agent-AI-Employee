import { motion } from 'motion/react'
import { AGENTS, QUICK_PROMPTS } from '../data/agents'
import AgentTicker from './AgentTicker'
import Composer from './Composer'

export default function EmptyState({ onSend }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="flex flex-1 flex-col items-center justify-center px-6"
    >
      <div className="flex w-full max-w-2xl flex-col items-center gap-8 text-center">
        <div className="space-y-3">
          <h1 className="font-display text-[2.75rem] leading-[1.1] text-ink">
            What should the <em className="text-clay italic">team</em> work on?
          </h1>
          <AgentTicker />
        </div>

        <div className="w-full">
          <Composer onSend={onSend} big />
        </div>

        <div className="flex flex-wrap items-center justify-center gap-2">
          {QUICK_PROMPTS.map((prompt) => {
            const agent = AGENTS.find((a) => a.id === prompt.agentId)
            return (
              <motion.button
                key={prompt.text}
                whileHover={{ y: -1 }}
                onClick={() => onSend(prompt.text)}
                className="flex items-center gap-1.5 rounded-full border border-line px-3.5 py-2 text-xs text-ink-soft transition-colors hover:border-clay hover:text-clay"
              >
                <span className="h-1.5 w-1.5 rounded-full" style={{ background: agent?.color }} />
                {prompt.text}
              </motion.button>
            )
          })}
        </div>
      </div>
    </motion.div>
  )
}
