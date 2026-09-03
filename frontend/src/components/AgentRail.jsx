import { AnimatePresence, motion } from 'motion/react'

export default function AgentRail({ agents, activeAgentId }) {
  return (
    <motion.div
      layout
      className="hidden items-center gap-1 rounded-2xl border border-line bg-paper/55 p-1 shadow-sm md:flex"
    >
      {agents.map((agent) => {
        const isActive = agent.id === activeAgentId
        return (
          <motion.div
            key={agent.id}
            layout
            whileHover={{ y: -1 }}
            className="relative"
            title={`${agent.name}: ${agent.role}`}
          >
            <AnimatePresence>
              {isActive && (
                <motion.span
                  layoutId="agent-rail-highlight"
                  className="absolute inset-0 rounded-xl bg-cream-soft"
                  initial={{ opacity: 0, scale: 0.92 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.92 }}
                  transition={{ type: 'spring', bounce: 0.18, duration: 0.45 }}
                />
              )}
            </AnimatePresence>

            <div className="relative flex h-9 items-center gap-2 rounded-xl px-1.5">
              <span
                className="relative grid h-7 w-7 shrink-0 place-items-center rounded-lg text-[11px] font-bold text-white shadow-sm"
                style={{ background: agent.color }}
              >
                {agent.initial}
                {isActive && (
                  <motion.span
                    className="absolute inset-0 rounded-lg"
                    style={{ border: `2px solid ${agent.color}` }}
                    animate={{ scale: [1, 1.55], opacity: [0.65, 0] }}
                    transition={{ duration: 1.4, repeat: Infinity, ease: 'easeOut' }}
                  />
                )}
              </span>

              <AnimatePresence initial={false}>
                {isActive && (
                  <motion.span
                    key="active-agent-name"
                    initial={{ opacity: 0, width: 0, x: -4 }}
                    animate={{ opacity: 1, width: 'auto', x: 0 }}
                    exit={{ opacity: 0, width: 0, x: -4 }}
                    transition={{ duration: 0.2, ease: 'easeOut' }}
                    className="overflow-hidden whitespace-nowrap pr-1 text-xs font-semibold"
                    style={{ color: agent.color }}
                  >
                    {agent.name}
                  </motion.span>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )
      })}
    </motion.div>
  )
}
