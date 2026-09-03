import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { UserRoundPlus, LogOut } from 'lucide-react'

export default function TopBar({ onAuthOpen, currentUser, onLogout }) {
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const handleLogoutClick = () => {
    onLogout()
    setDropdownOpen(false)
  }

  return (
    <motion.header
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="topbar-shell flex min-h-16 shrink-0 items-center justify-between px-4 sm:px-6 lg:px-5 relative z-30"
    >
      <motion.a
        href="/"
        whileHover={{ y: -1 }}
        whileTap={{ scale: 0.98 }}
        className="brand-wordmark font-display text-[1.85rem] font-semibold leading-none text-ink sm:text-[2rem]"
        aria-label="Chorus home"
      >
        Chorus
      </motion.a>

      <div className="relative">
        {!currentUser ? (
          <motion.button
            type="button"
            onClick={onAuthOpen}
            whileHover={{ y: -1, scale: 1.03 }}
            whileTap={{ scale: 0.94 }}
            className="account-button grid h-10 w-10 shrink-0 place-items-center rounded-xl text-ink transition-colors cursor-pointer"
            aria-label="Login or sign up"
            title="Login or sign up"
          >
            <UserRoundPlus size={20} strokeWidth={1.9} />
          </motion.button>
        ) : (
          <div>
            <motion.button
              type="button"
              onClick={() => setDropdownOpen(!dropdownOpen)}
              whileHover={{ y: -1, scale: 1.03 }}
              whileTap={{ scale: 0.94 }}
              className="grid h-10 w-10 shrink-0 place-items-center overflow-hidden rounded-xl text-white font-bold select-none cursor-pointer"
              style={{
                background: currentUser.picture
                  ? '#ffffff'
                  : currentUser.avatarColor || 'linear-gradient(135deg, #db7858 0%, #a64a36 100%)',
                boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 4px 12px rgba(0, 0, 0, 0.1)',
                fontSize: '0.85rem'
              }}
              aria-label="User menu"
              title={currentUser.name}
            >
              {currentUser.picture ? (
                <img
                  src={currentUser.picture}
                  alt=""
                  referrerPolicy="no-referrer"
                  className="h-full w-full object-cover"
                />
              ) : (
                currentUser.avatar
              )}
            </motion.button>

            <AnimatePresence>
              {dropdownOpen && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setDropdownOpen(false)}
                  />
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 8, scale: 0.95 }}
                    transition={{ duration: 0.15, ease: 'easeOut' }}
                    className="absolute right-0 mt-2 w-56 rounded-2xl border border-line bg-paper/95 p-3 shadow-2xl backdrop-blur-xl z-50 text-ink"
                  >
                    <div className="px-2 py-1.5 border-b border-line mb-2">
                      <p className="text-xs text-ink-soft font-medium leading-none">Signed in as</p>
                      <p className="text-sm font-semibold truncate mt-1 text-ink">{currentUser.name}</p>
                      <p className="text-[0.7rem] text-ink-soft truncate mt-0.5">{currentUser.email}</p>
                    </div>
                    <button
                      type="button"
                      onClick={handleLogoutClick}
                      className="w-full flex items-center gap-2 px-2 py-2 rounded-xl text-left text-xs font-semibold text-red-650 hover:bg-cream-soft transition-colors text-red-600 cursor-pointer"
                    >
                      <LogOut size={14} />
                      Sign out
                    </button>
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </motion.header>
  )
}
