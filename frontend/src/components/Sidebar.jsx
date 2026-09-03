import { useEffect, useMemo, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import {
  Clock3,
  MessageCircle,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  SquarePen,
  LogOut,
  Trash2,
  X,
} from 'lucide-react'

import ChorusMark from './ChorusMark'

// =========================================================
// NAVIGATION
// =========================================================

const primaryNav = [
  {
    label: 'New chat',
    icon: SquarePen,
  },
]

const railNav = [
  ...primaryNav,

  {
    label: 'Search',
    icon: Search,
  },

  {
    label: 'Recents',
    icon: Clock3,
  },
]

// =========================================================
// RAIL BUTTON
// =========================================================

function RailButton({
  icon: Icon,
  label,
  active = false,
  onClick,
}) {
  return (
    <motion.button
      type="button"
      onClick={onClick}
      whileHover={{
        scale: 1.08,
      }}
      whileTap={{
        scale: 0.92,
      }}
      className={`sidebar-rail-button ${
        active ? 'is-active' : ''
      }`}
      aria-label={label}
      title={label}
    >
      <Icon
        size={20}
        strokeWidth={1.9}
      />
    </motion.button>
  )
}

// =========================================================
// NAV ROW
// =========================================================

function NavRow({
  icon: Icon,
  label,
  active = false,
  onClick,
}) {
  return (
    <motion.button
      type="button"
      layout
      onClick={onClick}
      whileHover={{
        x: 3,
      }}
      whileTap={{
        scale: 0.985,
      }}
      className={`sidebar-nav-row ${
        active ? 'is-active' : ''
      }`}
    >
      <Icon
        size={19}
        strokeWidth={1.9}
      />

      <span>
        {label}
      </span>
    </motion.button>
  )
}

// =========================================================
// SIDEBAR
// =========================================================

export default function Sidebar({
  collapsed,
  onToggle,

  currentUser,
  onLogout,

  onNewChat,

  chats = [],
  activeChatId,

  onSelectChat,
  onDeleteChat,
}) {
  const [searchQuery, setSearchQuery] =
    useState('')

  const searchInputRef =
    useRef(null)

  const shouldFocusSearchRef =
    useRef(false)

  // =========================================================
  // SEARCH TERMS
  // =========================================================

  const normalizedSearchTerms =
    useMemo(() => {
      return searchQuery
        .trim()
        .toLowerCase()
        .split(/\s+/)
        .filter(Boolean)
    }, [searchQuery])

  // =========================================================
  // FILTER CHATS
  // =========================================================

  const filteredChats =
    useMemo(() => {
      if (
        normalizedSearchTerms.length === 0
      ) {
        return chats
      }

      return chats.filter((chat) => {
        const searchableText = [
          chat.title || 'New chat',

          ...(Array.isArray(
            chat.messages
          )
            ? chat.messages
            : []
          ).map(
            (message) =>
              message?.content || ''
          ),
        ]
          .join(' ')
          .toLowerCase()

        return normalizedSearchTerms.every(
          (term) =>
            searchableText.includes(
              term
            )
        )
      })
    }, [
      chats,
      normalizedSearchTerms,
    ])

  // =========================================================
  // SEARCH FOCUS
  // =========================================================

  useEffect(() => {
    if (
      collapsed ||
      !shouldFocusSearchRef.current
    ) {
      return
    }

    searchInputRef.current?.focus()

    shouldFocusSearchRef.current =
      false
  }, [collapsed])

  // =========================================================
  // SEARCH SHORTCUT
  // =========================================================

  const handleSearchShortcut = () => {
    if (collapsed) {
      shouldFocusSearchRef.current =
        true

      onToggle?.()

      return
    }

    searchInputRef.current?.focus()
  }

  // =========================================================
  // DELETE CHAT
  // =========================================================

  const handleDeleteChat = (
    event,
    chatId
  ) => {
    event.stopPropagation()

    onDeleteChat?.(chatId)
  }

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <motion.aside
      animate={{
        width: collapsed
          ? 78
          : 326,
      }}
      transition={{
        type: 'spring',
        bounce: 0.12,
        duration: 0.48,
      }}
      className={`dark-sidebar-shell ${
        collapsed
          ? 'is-collapsed'
          : 'is-open'
      }`}
    >
      <AnimatePresence
        mode="wait"
        initial={false}
      >

        {/* ================================================= */}
        {/* COLLAPSED SIDEBAR */}
        {/* ================================================= */}

        {collapsed ? (
          <motion.div
            key="collapsed-sidebar"

            initial={{
              opacity: 0,
              x: -10,
            }}

            animate={{
              opacity: 1,
              x: 0,
            }}

            exit={{
              opacity: 0,
              x: -10,
            }}

            transition={{
              duration: 0.2,
              ease: 'easeOut',
            }}

            className="flex h-full flex-col items-center py-4"
          >

            {/* BRAND */}

            <button
              type="button"
              onClick={onToggle}
              className="sidebar-rail-brand"
              aria-label="Expand sidebar"
              title="Expand sidebar"
            >
              <ChorusMark size={21} />
            </button>

            {/* RAIL NAV */}

            <nav
              className="mt-8 flex flex-col items-center gap-3"
              aria-label="Sidebar"
            >
              {railNav.map(
                (item) => (
                  <RailButton
                    key={item.label}
                    {...item}
                    onClick={
                      item.label ===
                      'New chat'
                        ? onNewChat
                        : item.label ===
                          'Search'
                          ? handleSearchShortcut
                          : item.label ===
                            'Recents'
                            ? onToggle
                            : undefined
                    }
                  />
                )
              )}
            </nav>

            {/* BOTTOM */}

            <div className="mt-auto flex flex-col items-center gap-3">

              <RailButton
                icon={
                  PanelLeftOpen
                }
                label="Open sidebar"
                onClick={
                  onToggle
                }
              />

              <button
                type="button"
                className="sidebar-avatar cursor-pointer overflow-hidden"
                style={
                  currentUser
                    ? {
                        background:
                          currentUser.avatarColor,
                      }
                    : undefined
                }
                aria-label={
                  currentUser
                    ? currentUser.name
                    : 'Guest Account'
                }
                title={
                  currentUser
                    ? currentUser.name
                    : 'Guest Account'
                }
              >
                {currentUser?.picture ? (
                  <img
                    src={
                      currentUser.picture
                    }
                    alt=""
                    referrerPolicy="no-referrer"
                    className="h-full w-full object-cover"
                  />
                ) : (
                  currentUser
                    ? currentUser.avatar
                    : 'G'
                )}
              </button>

            </div>
          </motion.div>

        ) : (

          /* ================================================= */
          /* OPEN SIDEBAR */
          /* ================================================= */

          <motion.div
            key="open-sidebar"

            initial={{
              opacity: 0,
              x: -16,
            }}

            animate={{
              opacity: 1,
              x: 0,
            }}

            exit={{
              opacity: 0,
              x: -16,
            }}

            transition={{
              duration: 0.22,
              ease: 'easeOut',
            }}

            className="flex h-full min-w-0 flex-col px-3 py-4"
          >

            {/* ================================================= */}
            {/* HEADER */}
            {/* ================================================= */}

            <div className="flex items-center justify-between px-1">

              <div className="flex min-w-0 items-center gap-3">

                <span className="sidebar-brand-mark">
                  <ChorusMark size={18} />
                </span>

                <div className="min-w-0">

                  <h2 className="sidebar-brand-title truncate font-display text-[1.45rem] font-semibold leading-none text-white">
                    Chorus
                  </h2>

                  <p className="sidebar-brand-kicker truncate font-display text-[0.73rem] font-medium italic leading-tight">
                    Plan • Act • Deliver
                  </p>

                </div>

              </div>

              <div className="flex items-center gap-1.5">

                <RailButton
                  icon={Search}
                  label="Search"
                  onClick={
                    handleSearchShortcut
                  }
                />

                <RailButton
                  icon={
                    PanelLeftClose
                  }
                  label="Close sidebar"
                  onClick={
                    onToggle
                  }
                />

              </div>
            </div>

            {/* ================================================= */}
            {/* PRIMARY NAVIGATION */}
            {/* ================================================= */}

            <nav
              className="mt-7 space-y-1.5"
              aria-label="Primary"
            >

              {primaryNav.map(
                (item) => (
                  <NavRow
                    key={item.label}
                    {...item}
                    active={
                      item.label ===
                      'New chat'
                    }
                    onClick={
                      item.label ===
                      'New chat'
                        ? onNewChat
                        : undefined
                    }
                  />
                )
              )}

              {/* SEARCH */}

              <div className="sidebar-search-field">

                <Search
                  size={19}
                  strokeWidth={1.9}
                  aria-hidden="true"
                />

                <input
                  ref={
                    searchInputRef
                  }
                  type="search"
                  value={
                    searchQuery
                  }
                  onChange={(
                    event
                  ) =>
                    setSearchQuery(
                      event.target
                        .value
                    )
                  }
                  placeholder="Search chats"
                  aria-label="Search chats"
                />

                {searchQuery && (
                  <button
                    type="button"
                    className="sidebar-search-clear"
                    onClick={() =>
                      setSearchQuery(
                        ''
                      )
                    }
                    aria-label="Clear search"
                    title="Clear search"
                  >
                    <X
                      size={14}
                      strokeWidth={2}
                    />
                  </button>
                )}

              </div>
            </nav>

            <div className="sidebar-divider" />

            {/* ================================================= */}
            {/* RECENTS */}
            {/* ================================================= */}

            <section className="flex min-h-0 flex-1 flex-col">

              <div className="sidebar-section-title">

                <span>
                  Recents
                </span>

                <Clock3 size={13} />

              </div>

              <div className="sidebar-recents-list mt-2 space-y-1 overflow-y-auto pr-1">

                <AnimatePresence
                  initial={false}
                >

                  {filteredChats.map(
                    (chat) => (
                      <motion.div
                        key={chat.id}
                        layout

                        initial={{
                          opacity: 0,
                          y: -5,
                        }}

                        animate={{
                          opacity: 1,
                          y: 0,
                        }}

                        exit={{
                          opacity: 0,
                          height: 0,
                          marginBottom: 0,
                        }}

                        className="group relative"
                      >

                        <button
                          type="button"

                          onClick={() =>
                            onSelectChat?.(
                              chat.id
                            )
                          }

                          className={`sidebar-recent-row w-full ${
                            chat.id ===
                            activeChatId
                              ? 'is-active'
                              : ''
                          }`}
                        >

                          <MessageCircle
                            size={16}
                            strokeWidth={1.9}
                          />

                          <span className="min-w-0 flex-1 truncate text-left">
                            {chat.title ||
                              'New chat'}
                          </span>

                          {/* DELETE */}

                          <span
                            className="ml-1 flex-shrink-0 cursor-pointer opacity-0 transition-opacity group-hover:opacity-100"
                            onClick={(
                              event
                            ) =>
                              handleDeleteChat(
                                event,
                                chat.id
                              )
                            }
                            role="button"
                            aria-label={`Delete ${
                              chat.title ||
                              'chat'
                            }`}
                            title="Delete chat"
                          >
                            <Trash2
                              size={14}
                              strokeWidth={1.8}
                            />
                          </span>

                        </button>

                      </motion.div>
                    )
                  )}

                </AnimatePresence>

                {/* EMPTY */}

                {chats.length === 0 && (
                  <div className="px-3 py-4 text-center text-xs text-white/35">
                    No conversations yet.
                  </div>
                )}

                {/* NO SEARCH RESULTS */}

                {chats.length > 0 &&
                  filteredChats.length ===
                    0 && (
                    <div className="px-3 py-4 text-center text-xs text-white/35">
                      No matching chats.
                    </div>
                  )}

              </div>
            </section>

            {/* ================================================= */}
            {/* USER */}
            {/* ================================================= */}

            <div className="mt-4 rounded-2xl border border-white/8 bg-white/[0.055] p-2">

              <div className="flex items-center gap-3">

                <span
                  className="sidebar-avatar overflow-hidden"
                  style={
                    currentUser
                      ? {
                          background:
                            currentUser.avatarColor,
                        }
                      : undefined
                  }
                >
                  {currentUser?.picture ? (
                    <img
                      src={
                        currentUser.picture
                      }
                      alt=""
                      referrerPolicy="no-referrer"
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    currentUser
                      ? currentUser.avatar
                      : 'G'
                  )}
                </span>

                <div className="min-w-0 flex-1">

                  <p className="truncate text-[0.82rem] font-semibold text-white">
                    {currentUser
                      ? currentUser.name
                      : 'Guest User'}
                  </p>

                  <p className="truncate text-[0.72rem] text-white/42">
                    {currentUser
                      ? currentUser.email
                      : 'Not signed in'}
                  </p>

                </div>

                {currentUser && (
                  <motion.button
                    type="button"
                    onClick={
                      onLogout
                    }

                    whileHover={{
                      rotate: 18,
                      scale: 1.06,
                    }}

                    whileTap={{
                      scale: 0.92,
                    }}

                    className="sidebar-mini-button cursor-pointer text-white/60 transition-colors hover:text-white"

                    aria-label="Logout"
                    title="Logout"
                  >
                    <LogOut
                      size={16}
                    />
                  </motion.button>
                )}

              </div>
            </div>

          </motion.div>
        )}

      </AnimatePresence>
    </motion.aside>
  )
}