import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import {
  ArrowUp,
  BarChart3,
  Check,
  ChevronDown,
  Code2,
  FileText,
  ImagePlus,
  PenLine,
  Search,
  X,
} from 'lucide-react'

const CHAT_MODES = [
  {
    id: 'research',
    label: 'Research',
    icon: Search,
    color: 'var(--color-agent-research)',
  },
  {
    id: 'code',
    label: 'Code',
    icon: Code2,
    color: 'var(--color-agent-code)',
  },
  {
    id: 'write',
    label: 'Write',
    icon: PenLine,
    color: 'var(--color-agent-writing)',
  },
  {
    id: 'analyze',
    label: 'Analyze',
    icon: BarChart3,
    color: 'var(--color-clay)',
  },
]

export default function Composer({
  onSend,
  big = false,
}) {
  const [value, setValue] = useState('')
  const [attachedFiles, setAttachedFiles] = useState([])
  const [modeOpen, setModeOpen] = useState(false)
  const [selectedMode, setSelectedMode] =
    useState(CHAT_MODES[0])

  const fileInputRef = useRef(null)
  const modeSelectorRef = useRef(null)
  const textareaRef = useRef(null)

  // =========================================================
  // TEXTAREA HEIGHT
  // =========================================================

  useEffect(() => {
    const el = textareaRef.current

    if (!el) {
      return
    }

    el.style.height = 'auto'

    el.style.height = `${Math.min(
      el.scrollHeight,
      200
    )}px`
  }, [value])

  // =========================================================
  // CLOSE MODE MENU
  // =========================================================

  useEffect(() => {
    if (!modeOpen) {
      return
    }

    const closeOnOutsideClick = (event) => {
      if (
        !modeSelectorRef.current?.contains(
          event.target
        )
      ) {
        setModeOpen(false)
      }
    }

    const closeOnEscape = (event) => {
      if (event.key === 'Escape') {
        setModeOpen(false)
      }
    }

    document.addEventListener(
      'pointerdown',
      closeOnOutsideClick
    )

    document.addEventListener(
      'keydown',
      closeOnEscape
    )

    return () => {
      document.removeEventListener(
        'pointerdown',
        closeOnOutsideClick
      )

      document.removeEventListener(
        'keydown',
        closeOnEscape
      )
    }
  }, [modeOpen])

  // =========================================================
  // SUBMIT
  // =========================================================

  const submit = () => {
    const trimmed = value.trim()

    if (!trimmed) {
      return
    }

    /*
     * IMPORTANT:
     *
     * Send the actual File objects together with the
     * user's request.
     *
     * useChat.js will upload/process them before
     * sending the chat request.
     */
    onSend(trimmed, {
      files: attachedFiles,
      mode: selectedMode.id,
    })

    setValue('')
    setAttachedFiles([])

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // =========================================================
  // KEYBOARD
  // =========================================================

  const handleKeyDown = (event) => {
    if (
      event.key === 'Enter' &&
      !event.shiftKey
    ) {
      event.preventDefault()
      submit()
    }
  }

  // =========================================================
  // FILE SELECTION
  // =========================================================

  const handleFileChange = (event) => {
    const files = Array.from(
      event.target.files ?? []
    )

    if (!files.length) {
      return
    }

    setAttachedFiles(files)
  }

  // =========================================================
  // REMOVE ATTACHMENT
  // =========================================================

  const removeFile = (index) => {
    setAttachedFiles((previous) =>
      previous.filter(
        (_, fileIndex) =>
          fileIndex !== index
      )
    )

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const SelectedIcon = selectedMode.icon

  return (
    <div
      className={`composer-shell relative flex flex-col justify-between gap-3 rounded-[28px] border border-line bg-paper p-3 shadow-[0_10px_30px_-12px_rgba(61,57,41,0.2)] ${
        big
          ? 'min-h-[144px] px-4 pt-4'
          : 'min-h-[118px]'
      }`}
    >
      {/* =================================================
          ATTACHMENT PREVIEW
         ================================================= */}

      <AnimatePresence initial={false}>
        {attachedFiles.length > 0 && (
          <motion.div
            initial={{
              opacity: 0,
              height: 0,
              y: -4,
            }}
            animate={{
              opacity: 1,
              height: 'auto',
              y: 0,
            }}
            exit={{
              opacity: 0,
              height: 0,
              y: -4,
            }}
            className="overflow-hidden"
          >
            <div className="flex flex-wrap gap-2 px-1 pt-1">
              {attachedFiles.map(
                (file, index) => (
                  <motion.div
                    key={`${file.name}-${file.lastModified}-${index}`}
                    initial={{
                      opacity: 0,
                      scale: 0.96,
                    }}
                    animate={{
                      opacity: 1,
                      scale: 1,
                    }}
                    className="flex max-w-full items-center gap-2 rounded-xl border border-line bg-ink/[0.03] px-2.5 py-2"
                  >
                    <FileText
                      size={15}
                      strokeWidth={2}
                      className="shrink-0 text-ink/60"
                    />

                    <span className="max-w-[220px] truncate text-xs font-medium text-ink/75">
                      {file.name}
                    </span>

                    <button
                      type="button"
                      onClick={() =>
                        removeFile(index)
                      }
                      className="grid h-5 w-5 shrink-0 place-items-center rounded-full text-ink/45 transition hover:bg-ink/10 hover:text-ink"
                      aria-label={`Remove ${file.name}`}
                      title={`Remove ${file.name}`}
                    >
                      <X
                        size={12}
                        strokeWidth={2}
                      />
                    </button>
                  </motion.div>
                )
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* =================================================
          TEXT INPUT
         ================================================= */}

      <textarea
        ref={textareaRef}
        rows={1}
        value={value}
        onChange={(event) =>
          setValue(event.target.value)
        }
        onKeyDown={handleKeyDown}
        placeholder="Start a task with Chorus..."
        className="composer-input max-h-48 min-h-11 w-full resize-none bg-transparent px-2 py-1.5 text-[15px] leading-relaxed text-ink placeholder:text-ink-faint"
      />

      {/* =================================================
          CONTROLS
         ================================================= */}

      <div className="flex items-center justify-between gap-3 px-1">
        <div className="flex min-w-0 flex-wrap items-center gap-2">
          {/* FILE INPUT */}

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={[
              'image/*',
              '.pdf',
              '.doc',
              '.docx',
              '.txt',
              '.csv',
              '.xls',
              '.xlsx',
              'application/pdf',
              'application/msword',
              'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
              'text/plain',
              'text/csv',
              'application/vnd.ms-excel',
              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            ].join(',')}
            onChange={handleFileChange}
            className="sr-only"
          />

          {/* UPLOAD BUTTON */}

          <motion.button
            type="button"
            onClick={() =>
              fileInputRef.current?.click()
            }
            whileHover={{ y: -1 }}
            whileTap={{ scale: 0.94 }}
            className="composer-icon-button relative grid h-8 w-8 shrink-0 place-items-center rounded-full"
            aria-label="Upload a file"
            title="Upload a file"
          >
            <ImagePlus
              size={16}
              strokeWidth={2}
            />

            {attachedFiles.length > 0 && (
              <span className="composer-file-count">
                {attachedFiles.length}
              </span>
            )}
          </motion.button>

          {/* MODE SELECTOR */}

          <div
            ref={modeSelectorRef}
            className="relative"
          >
            <motion.button
              type="button"
              onClick={() =>
                setModeOpen(
                  (open) => !open
                )
              }
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.98 }}
              className="composer-mode-trigger inline-flex h-8 items-center gap-2 rounded-full px-2.5 pr-2"
              aria-haspopup="listbox"
              aria-expanded={modeOpen}
            >
              <span
                className="composer-mode-icon"
                style={{
                  '--mode-color':
                    selectedMode.color,
                }}
              >
                <SelectedIcon
                  size={13}
                  strokeWidth={2}
                />
              </span>

              <span>
                {selectedMode.label}
              </span>

              <ChevronDown
                size={13}
                strokeWidth={2}
                className={`transition-transform ${
                  modeOpen
                    ? 'rotate-180'
                    : ''
                }`}
              />
            </motion.button>

            <AnimatePresence>
              {modeOpen && (
                <motion.div
                  initial={{
                    opacity: 0,
                    y: 8,
                    scale: 0.98,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                    scale: 1,
                  }}
                  exit={{
                    opacity: 0,
                    y: 8,
                    scale: 0.98,
                  }}
                  transition={{
                    duration: 0.18,
                    ease: 'easeOut',
                  }}
                  className="composer-mode-menu absolute bottom-11 left-0 z-20 w-44 rounded-2xl border border-line bg-paper p-1.5 shadow-[0_18px_42px_-24px_rgba(61,57,41,0.55)]"
                  role="listbox"
                >
                  {CHAT_MODES.map(
                    (mode) => {
                      const Icon =
                        mode.icon

                      const isSelected =
                        mode.id ===
                        selectedMode.id

                      return (
                        <button
                          key={mode.id}
                          type="button"
                          onClick={() => {
                            setSelectedMode(
                              mode
                            )

                            setModeOpen(
                              false
                            )
                          }}
                          className={`composer-mode-option flex w-full items-center gap-2 rounded-xl px-2.5 py-2 text-left ${
                            isSelected
                              ? 'is-selected'
                              : ''
                          }`}
                          role="option"
                          aria-selected={
                            isSelected
                          }
                        >
                          <span
                            className="composer-mode-icon"
                            style={{
                              '--mode-color':
                                mode.color,
                            }}
                          >
                            <Icon
                              size={13}
                              strokeWidth={2}
                            />
                          </span>

                          <span className="min-w-0 flex-1 truncate">
                            {mode.label}
                          </span>

                          {isSelected && (
                            <Check
                              size={13}
                              strokeWidth={2.2}
                            />
                          )}
                        </button>
                      )
                    }
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* SEND */}

        <motion.button
          type="button"
          onClick={submit}
          disabled={!value.trim()}
          whileHover={
            value.trim()
              ? { scale: 1.05 }
              : {}
          }
          whileTap={
            value.trim()
              ? { scale: 0.92 }
              : {}
          }
          className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-clay text-white transition-colors disabled:cursor-not-allowed disabled:bg-ink-faint"
          aria-label="Send message"
        >
          <ArrowUp size={16} />
        </motion.button>
      </div>
    </div>
  )
}