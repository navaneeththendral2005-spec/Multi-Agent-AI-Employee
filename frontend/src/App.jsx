import { useState } from 'react'
import {
  AnimatePresence,
  motion,
} from 'motion/react'

import Sidebar from './components/Sidebar'
import TopBar from './components/TopBar'
import ChatView from './components/ChatView'
import Preloader from './components/Preloader'
import AuthPage from './components/AuthPage'

import { useChat } from './hooks/useChat'

export default function App() {
  // =========================================================
  // APPLICATION STATE
  // =========================================================

  const [isLoading, setIsLoading] =
    useState(true)

  const [sidebarCollapsed, setSidebarCollapsed] =
    useState(true)

  const [authOpen, setAuthOpen] =
    useState(false)

  // =========================================================
  // CHAT STATE
  // =========================================================

  const {
    conversations,
    activeChatId,
    messages,
    thinkingAgentId,

    sendMessage,
    newChat,
    selectChat,
    deleteChat,
  } = useChat()

  // =========================================================
  // USER
  // =========================================================

  const [currentUser, setCurrentUser] =
    useState(() => {
      try {
        const saved =
          localStorage.getItem(
            'chorus-user'
          )

        return saved
          ? JSON.parse(saved)
          : null
      } catch {
        return null
      }
    })

  // =========================================================
  // AUTH
  // =========================================================

  const handleLogin = (user) => {
    setCurrentUser(user)

    localStorage.setItem(
      'chorus-user',
      JSON.stringify(user)
    )
  }

  const handleLogout = () => {
    setCurrentUser(null)

    localStorage.removeItem(
      'chorus-user'
    )
  }

  // =========================================================
  // NEW CHAT
  // =========================================================

  const handleNewChat = () => {
    newChat()
  }

  // =========================================================
  // SELECT CHAT
  // =========================================================

  const handleSelectChat = (chatId) => {
    selectChat(chatId)
  }

  // =========================================================
  // DELETE CHAT
  // =========================================================

  const handleDeleteChat = (chatId) => {
    deleteChat(chatId)
  }

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <>
      {/* =================================================== */}
      {/* PRELOADER */}
      {/* =================================================== */}

      <AnimatePresence mode="wait">
        {isLoading && (
          <Preloader
            key="preloader"
            duration={4000}
            onComplete={() =>
              setIsLoading(false)
            }
          />
        )}
      </AnimatePresence>

      {/* =================================================== */}
      {/* MAIN APPLICATION */}
      {/* =================================================== */}

      <motion.div
        initial={{
          opacity: 0,
        }}
        animate={{
          opacity: isLoading
            ? 0
            : 1,

          scale: authOpen
            ? 0.985
            : 1,

          filter: authOpen
            ? 'blur(8px)'
            : 'blur(0px)',
        }}
        transition={{
          duration: 0.6,
          ease: 'easeOut',
        }}
        className="flex h-screen w-screen overflow-hidden bg-cream font-sans text-ink"
      >
        {/* ================================================= */}
        {/* SIDEBAR */}
        {/* ================================================= */}

        <Sidebar
          collapsed={
            sidebarCollapsed
          }

          onToggle={() =>
            setSidebarCollapsed(
              (value) => !value
            )
          }

          currentUser={
            currentUser
          }

          onLogout={
            handleLogout
          }

          onNewChat={
            handleNewChat
          }

          chats={
            conversations
          }

          activeChatId={
            activeChatId
          }

          onSelectChat={
            handleSelectChat
          }

          onDeleteChat={
            handleDeleteChat
          }
        />

        {/* ================================================= */}
        {/* MAIN CONTENT */}
        {/* ================================================= */}

        <div className="flex min-w-0 flex-1 flex-col">
          <TopBar
            onAuthOpen={() =>
              setAuthOpen(true)
            }

            currentUser={
              currentUser
            }

            onLogout={
              handleLogout
            }
          />

          <ChatView
            messages={
              messages
            }

            thinkingAgentId={
              thinkingAgentId
            }

            onSend={
              sendMessage
            }
          />
        </div>
      </motion.div>

      {/* =================================================== */}
      {/* AUTH */}
      {/* =================================================== */}

      <AnimatePresence>
        {authOpen && (
          <AuthPage
            key="auth-page"

            onClose={() =>
              setAuthOpen(false)
            }

            onLogin={
              handleLogin
            }
          />
        )}
      </AnimatePresence>
    </>
  )
}