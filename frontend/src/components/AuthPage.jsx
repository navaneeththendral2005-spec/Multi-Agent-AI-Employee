import { useCallback, useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { X } from 'lucide-react'

const GOOGLE_SCRIPT_SRC = 'https://accounts.google.com/gsi/client'
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''
let googleScriptPromise

const copy = {
  signIn: {
    title: 'Sign In',
    subtitle: 'Please enter your details to sign in.',
    button: 'Sign in',
    footer: "Don't have an account?",
    footerAction: 'Sign up',
  },
  signUp: {
    title: 'Sign Up',
    subtitle: 'Create your Chorus account to continue.',
    button: 'Sign up',
    footer: 'Already have an account?',
    footerAction: 'Sign in',
  },
}

function DotRing() {
  return (
    <span className="auth-dot-ring" aria-hidden="true">
      {Array.from({ length: 10 }).map((_, index) => (
        <i key={index} style={{ '--dot-index': index }} />
      ))}
    </span>
  )
}

function GoogleMark() {
  return (
    <span className="google-mark" aria-hidden="true">
      G
    </span>
  )
}

function loadGoogleIdentity() {
  if (window.google?.accounts?.id) {
    return Promise.resolve(window.google)
  }

  if (googleScriptPromise) {
    return googleScriptPromise
  }

  googleScriptPromise = new Promise((resolve, reject) => {
    const existingScript = document.querySelector(`script[src="${GOOGLE_SCRIPT_SRC}"]`)

    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(window.google), { once: true })
      existingScript.addEventListener('error', reject, { once: true })
      return
    }

    const script = document.createElement('script')
    script.src = GOOGLE_SCRIPT_SRC
    script.async = true
    script.defer = true
    script.onload = () => resolve(window.google)
    script.onerror = reject
    document.head.appendChild(script)
  })

  return googleScriptPromise
}

function decodeGoogleCredential(credential) {
  const [, payload] = credential.split('.')
  const normalizedPayload = payload.replace(/-/g, '+').replace(/_/g, '/')
  const decodedPayload = decodeURIComponent(
    atob(normalizedPayload)
      .split('')
      .map((char) => `%${char.charCodeAt(0).toString(16).padStart(2, '0')}`)
      .join(''),
  )

  return JSON.parse(decodedPayload)
}

function buildUserFromEmail(email, nameOverride = '', provider = 'email') {
  const normalizedEmail = String(email || '').trim().toLowerCase()
  const baseName = (nameOverride || normalizedEmail.split('@')[0] || 'Google User').trim()
  const displayName = baseName
    .replace(/[._-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
  const initials = displayName
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || 'G')
    .join('') || 'G'

  const palette = [
    'linear-gradient(135deg, #d78558 0%, #b15f45 100%)',
    'linear-gradient(135deg, #6d8dff 0%, #4d66db 100%)',
    'linear-gradient(135deg, #4cbf9b 0%, #2d8a7f 100%)',
    'linear-gradient(135deg, #c873d1 0%, #8f4ab7 100%)',
    'linear-gradient(135deg, #ff9d7a 0%, #d7684e 100%)',
    'linear-gradient(135deg, #7f8aa8 0%, #4d6078 100%)',
  ]

  const colorIndex = Math.abs(normalizedEmail.length + displayName.length) % palette.length

  return {
    id: `${provider}-${normalizedEmail || 'account'}-${Date.now()}`,
    name: displayName || 'Google User',
    email: normalizedEmail || 'account@example.com',
    avatar: initials.slice(0, 2),
    avatarColor: palette[colorIndex],
    provider,
  }
}

function buildUserFromGoogleCredential(credential) {
  const profile = decodeGoogleCredential(credential)
  const email = String(profile.email || '').trim().toLowerCase()
  const fallbackName = email ? email.split('@')[0] : 'Google User'
  const baseUser = buildUserFromEmail(email, profile.name || fallbackName, 'google')

  return {
    ...baseUser,
    id: `google-${profile.sub || email || Date.now()}`,
    picture: profile.picture || '',
  }
}

export default function AuthPage({ onClose, onLogin }) {
  const [mode, setMode] = useState('signIn')
  const [googleStatus, setGoogleStatus] = useState(GOOGLE_CLIENT_ID ? 'loading' : 'needs-config')
  const [googleMessage, setGoogleMessage] = useState('')
  const googleButtonRef = useRef(null)
  const isSignIn = mode === 'signIn'
  const content = copy[mode]

  const applyLogin = useCallback((user) => {
    onLogin?.(user)
    onClose?.()
  }, [onClose, onLogin])

  useEffect(() => {
    let isMounted = true

    if (!GOOGLE_CLIENT_ID) {
      return undefined
    }

    loadGoogleIdentity()
      .then((google) => {
        if (!isMounted || !google?.accounts?.id) {
          return
        }

        google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: (response) => {
            try {
              if (!response.credential) {
                setGoogleMessage('Google did not return an account credential.')
                return
              }

              applyLogin(buildUserFromGoogleCredential(response.credential))
            } catch {
              setGoogleMessage('Google sign-in could not finish.')
            }
          },
          auto_select: false,
          cancel_on_tap_outside: true,
        })

        if (googleButtonRef.current) {
          const buttonWidth = Math.floor(googleButtonRef.current.getBoundingClientRect().width || 276)
          googleButtonRef.current.innerHTML = ''
          google.accounts.id.renderButton(googleButtonRef.current, {
            type: 'standard',
            theme: 'filled_black',
            size: 'large',
            shape: 'pill',
            text: isSignIn ? 'signin_with' : 'signup_with',
            logo_alignment: 'left',
            width: buttonWidth,
          })
        }

        setGoogleStatus('ready')
      })
      .catch(() => {
        if (!isMounted) {
          return
        }

        setGoogleStatus('error')
        setGoogleMessage('Google sign-in is unavailable right now.')
      })

    return () => {
      isMounted = false
    }
  }, [applyLogin, isSignIn])

  function handleGoogleContinue() {
    if (!GOOGLE_CLIENT_ID) {
      setGoogleMessage('Add VITE_GOOGLE_CLIENT_ID to enable Google accounts.')
      return
    }

    setGoogleMessage('Google sign-in is still loading.')
  }

  function handleSubmit(event) {
    event.preventDefault()

    const formData = new FormData(event.currentTarget)
    const email = String(formData.get('email') || '').trim().toLowerCase()
    const password = String(formData.get('password') || '')
    const confirmPassword = String(formData.get('confirm-password') || '')
    const name = String(formData.get('name') || '').trim()

    if (!email || !password) {
      return
    }

    if (!isSignIn && password !== confirmPassword) {
      return
    }

    const user = buildUserFromEmail(email, isSignIn ? email.split('@')[0] : name, 'email')
    applyLogin(user)
  }

  return (
    <motion.section
      className="auth-page fixed inset-0 z-50 grid min-h-screen place-items-center overflow-hidden px-4 py-8 font-sans text-white"
      initial={{ opacity: 0, clipPath: 'circle(0% at calc(100% - 44px) 32px)' }}
      animate={{ opacity: 1, clipPath: 'circle(150% at calc(100% - 44px) 32px)' }}
      exit={{ opacity: 0, clipPath: 'circle(0% at calc(100% - 44px) 32px)' }}
      transition={{ duration: 0.72, ease: [0.22, 1, 0.36, 1] }}
      role="dialog"
      aria-modal="true"
      aria-label="Account access"
    >
      <motion.button
        type="button"
        onClick={onClose}
        whileHover={{ y: -1, scale: 1.04 }}
        whileTap={{ scale: 0.94 }}
        className="auth-close-button"
        aria-label="Close account page"
        title="Close"
      >
        <X size={18} strokeWidth={1.9} />
      </motion.button>

      <motion.div
        className={`auth-card ${isSignIn ? 'is-sign-in' : 'is-sign-up'}`}
        initial={{ opacity: 0, y: 28, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 18, scale: 0.97 }}
        transition={{ delay: 0.12, duration: 0.52, ease: [0.22, 1, 0.36, 1] }}
      >
        <DotRing />

        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={mode}
            initial={{ opacity: 0, x: isSignIn ? -18 : 18 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: isSignIn ? 18 : -18 }}
            transition={{ duration: 0.28, ease: 'easeOut' }}
            className="auth-content"
          >
            <header className="text-center">
              <h1 className="auth-title">{content.title}</h1>
              <p className="auth-subtitle">{content.subtitle}</p>
            </header>

            <form className="auth-form" onSubmit={handleSubmit}>
              {!isSignIn && (
                <input
                  className="auth-input"
                  type="text"
                  name="name"
                  autoComplete="name"
                  placeholder="Full name"
                  aria-label="Full name"
                  required
                />
              )}

              <input
                className="auth-input"
                type="email"
                name="email"
                autoComplete="email"
                placeholder="Enter your email address"
                aria-label="Email address"
                required
              />

              <input
                className="auth-input"
                type="password"
                name="password"
                autoComplete={isSignIn ? 'current-password' : 'new-password'}
                placeholder="Password"
                aria-label="Password"
                required
              />

              {!isSignIn && (
                <input
                  className="auth-input"
                  type="password"
                  name="confirm-password"
                  autoComplete="new-password"
                  placeholder="Confirm password"
                  aria-label="Confirm password"
                  required
                />
              )}

              {isSignIn && (
                <button type="button" className="auth-link-button auth-forgot">
                  Forgot Password?
                </button>
              )}

              <button type="submit" className="auth-primary-button">
                {content.button}
              </button>
            </form>

            <div className="auth-divider">
              <span />
              <em>OR</em>
              <span />
            </div>

            <div className="auth-google-slot">
              {GOOGLE_CLIENT_ID ? (
                <div
                  ref={googleButtonRef}
                  className={`auth-google-native ${googleStatus === 'loading' ? 'is-loading' : ''}`}
                />
              ) : (
                <button type="button" className="auth-google-button" onClick={handleGoogleContinue}>
                  <GoogleMark />
                  Connect Google Account
                </button>
              )}
            </div>

            {googleMessage && (
              <p className="auth-status-message" role="status">
                {googleMessage}
              </p>
            )}

            <p className="auth-footer">
              {content.footer}{' '}
              <button
                type="button"
                className="auth-link-button"
                onClick={() => {
                  setGoogleMessage('')
                  setMode(isSignIn ? 'signUp' : 'signIn')
                }}
              >
                {content.footerAction}
              </button>
            </p>
          </motion.div>
        </AnimatePresence>
      </motion.div>
    </motion.section>
  )
}
