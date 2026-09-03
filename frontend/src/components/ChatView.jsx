import { useEffect, useRef } from 'react'
import { AnimatePresence } from 'motion/react'
import EmptyState from './EmptyState'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import Composer from './Composer'

export default function ChatView({ messages, thinkingAgentId, onSend }) {
  const scrollRef = useRef(null)

  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [messages, thinkingAgentId])

  if (messages.length === 0) {
    return <EmptyState onSend={onSend} />
  }

  return (
    <>
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-6">
          <AnimatePresence>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {thinkingAgentId && <TypingIndicator key="typing" agentId={thinkingAgentId} />}
          </AnimatePresence>
        </div>
      </div>
      <div className="shrink-0 border-t border-line px-6 py-4">
        <div className="mx-auto max-w-3xl">
          <Composer onSend={onSend} />
        </div>
      </div>
    </>
  )
}
