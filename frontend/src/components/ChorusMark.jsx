export default function ChorusMark({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="8" cy="12" r="4" fill="var(--color-clay)" />
      <circle cx="14" cy="8" r="4" fill="#E8C4A0" />
      <circle cx="16" cy="15" r="4" fill="var(--color-cream)" fillOpacity="0.9" />
    </svg>
  )
}
