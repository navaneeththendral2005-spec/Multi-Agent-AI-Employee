import { useState, useEffect } from 'react'
import { motion } from 'motion/react'

export default function Preloader({ onComplete, duration = 4000 }) {
  const [progress, setProgress] = useState(0)
  const [stageText, setStageText] = useState('Initializing workspace...')

  useEffect(() => {
    const startTime = performance.now()

    const updateProgress = (currentTime) => {
      const elapsed = currentTime - startTime
      const currentPercent = Math.min(100, (elapsed / duration) * 100)
      setProgress(currentPercent)

      if (currentPercent < 30) {
        setStageText('Initializing agent workspace...')
      } else if (currentPercent < 65) {
        setStageText('Connecting neural coordinator...')
      } else if (currentPercent < 90) {
        setStageText('Harmonizing agent team...')
      } else {
        setStageText('Ready to collaborate')
      }

      if (elapsed < duration) {
        requestAnimationFrame(updateProgress)
      } else {
        setProgress(100)
        const timeout = setTimeout(() => {
          if (onComplete) onComplete()
        }, 150)
        return () => clearTimeout(timeout)
      }
    }

    const animFrame = requestAnimationFrame(updateProgress)
    return () => cancelAnimationFrame(animFrame)
  }, [duration, onComplete])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{
        opacity: 0,
        scale: 1.04,
        filter: 'blur(12px)',
        transition: { duration: 0.85, ease: [0.22, 1, 0.36, 1] },
      }}
      transition={{ duration: 0.5 }}
      className="preloader-backdrop fixed inset-0 z-[9999] flex h-screen w-screen select-none flex-col items-center justify-center overflow-hidden"
      role="progressbar"
      aria-valuenow={Math.round(progress)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label="Loading Chorus"
    >
      {/* Background Image Layer (Subtle Black & Pearl White static art) */}
      <div
        className="preloader-image-layer pointer-events-none absolute inset-0 transform scale-105"
        style={{
          backgroundImage: `radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 60%), url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=2000&q=85')`,
        }}
      />

      {/* Atmospheric Vignette & Lighting */}
      <div className="preloader-vignette pointer-events-none absolute inset-0" />
      <div className="preloader-glow-orb pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[580px] h-[580px] rounded-full blur-3xl opacity-60" />

      {/* Subtle Harmonic Waveform Rings */}
      <div className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
        <motion.div
          animate={{
            scale: [1, 1.08, 1],
            opacity: [0.15, 0.3, 0.15],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="h-[320px] w-[320px] sm:h-[420px] sm:w-[420px] rounded-full border border-white/10"
        />
        <motion.div
          animate={{
            scale: [1.06, 0.98, 1.06],
            opacity: [0.1, 0.22, 0.1],
          }}
          transition={{
            duration: 3.8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute h-[240px] w-[240px] sm:h-[310px] sm:w-[310px] rounded-full border border-[var(--color-clay)]/20"
        />
      </div>

      {/* Main Center Content */}
      <div className="relative z-10 flex flex-col items-center px-6 text-center">
        {/* Chorus Emblem */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0, y: -10 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="mb-5 flex items-center justify-center"
        >
          <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.03] shadow-2xl backdrop-blur-md">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle cx="8" cy="12" r="4" fill="var(--color-clay)" />
              <circle cx="14" cy="8" r="4" fill="#E8C4A0" />
              <circle cx="16" cy="15" r="4" fill="#F4F1EA" fillOpacity="0.95" />
            </svg>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
              className="absolute inset-0 rounded-2xl border border-white/15"
            />
          </div>
        </motion.div>

        {/* Project Name: Chorus */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-col items-center"
        >
          <h1 className="pearl-heading font-display text-5xl font-semibold tracking-tight text-white sm:text-6xl md:text-7xl">
            <span className="text-[var(--color-clay)]">C</span>horus
          </h1>

          {/* Slogan: Plan • Act • Deliver */}
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.35, ease: 'easeOut' }}
            className="mt-3.5 flex items-center gap-2.5 font-sans text-[0.8rem] font-medium tracking-[0.38em] uppercase text-[#D8D4C7] sm:text-sm sm:tracking-[0.45em]"
          >
            <span>Plan</span>
            <span className="text-[var(--color-clay)] font-bold opacity-80">•</span>
            <span>Act</span>
            <span className="text-[var(--color-clay)] font-bold opacity-80">•</span>
            <span>Deliver</span>
          </motion.div>
        </motion.div>

        {/* Loading Progress Bar & Status */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5, ease: 'easeOut' }}
          className="mt-10 flex flex-col items-center gap-3"
        >
          {/* Fine Hairline Progress Track */}
          <div className="progress-track relative h-[2.5px] w-56 overflow-hidden rounded-full sm:w-68">
            <div
              className="progress-fill h-full transition-[width] duration-100 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Status Subtitle & Percentage */}
          <div className="flex w-56 sm:w-68 items-center justify-between text-[0.72rem] font-sans text-white/40">
            <span className="font-light tracking-wide text-white/60 transition-all duration-300">
              {stageText}
            </span>
            <span className="font-mono text-white/50">{Math.round(progress)}%</span>
          </div>
        </motion.div>
      </div>

      {/* Subtle Bottom Watermark */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.6 }}
        className="absolute bottom-6 flex items-center gap-2 text-[0.68rem] tracking-widest uppercase text-white/20 font-sans"
      >
        <span>Multi-Agent AI Workspace</span>
      </motion.div>
    </motion.div>
  )
}
