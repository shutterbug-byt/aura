import { useId, useState } from 'react'
import ParticleField from './components/ParticleField'
import { WORDMARK_LETTERS, WORDMARK_STROKE, WORDMARK_VIEWBOX } from './components/wordmarkGeometry'
import './App.css'

type IconName = 'home' | 'explore' | 'tools' | 'settings' | 'spark' | 'circle'
function Icon({ name }: { name: IconName }) {
  const paths: Record<IconName, React.ReactNode> = {
    home: <><path d="m3 10 9-7 9 7v10H7V10" /><path d="M10 20v-6h5v6" /></>,
    explore: <><circle cx="12" cy="12" r="9" /><path d="m16 8-2.5 5.5L8 16l2.5-5.5Z" /></>,
    tools: <><rect x="4" y="4" width="6" height="6" rx="1" /><rect x="14" y="4" width="6" height="6" rx="1" /><rect x="4" y="14" width="6" height="6" rx="1" /><rect x="14" y="14" width="6" height="6" rx="1" /></>,
    settings: <><path d="M4 7h16M4 17h16" /><circle cx="9" cy="7" r="2" /><circle cx="15" cy="17" r="2" /></>,
    spark: <path d="M12 2c0 7-3 10-10 10 7 0 10 3 10 10 0-7 3-10 10-10-7 0-10-3-10-10Z" />,
    circle: <><circle cx="12" cy="12" r="7" /><circle cx="12" cy="12" r="2" /></>,
  }
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>
}

const navItems = ['Home', 'Explore', 'Tools', 'Settings'] as const
const navIcons: IconName[] = ['home', 'explore', 'tools', 'settings']

function App() {
  const wordmarkLettersId = useId()
  const reflectionFadeId = useId()
  const reflectionMaskId = useId()
  const reflectionBlurId = useId()
  const horizonId = useId()
  const [message, setMessage] = useState('')
  const [active, setActive] = useState<string>('Home')

  return (
    <main className="aura-app">
      <ParticleField />
      <header className="topbar">
        <div className="top-actions" aria-label="Assistant controls">
          <button type="button" aria-label="Assistant options (unavailable)" aria-disabled="true" title="Assistant options are not connected"><Icon name="spark" /></button>
          <button type="button" aria-label="Session controls (unavailable)" aria-disabled="true" title="Session controls are not connected"><Icon name="circle" /></button>
          <button type="button" aria-label="Settings (unavailable)" aria-disabled="true" title="Settings are not connected"><Icon name="settings" /></button>
        </div>
      </header>

      <section className="hero" aria-labelledby="aura-title">
        <h1 id="aura-title" className="aura-title" aria-label="AURA">
          <svg className="aura-wordmark" viewBox={`${WORDMARK_VIEWBOX.x} ${WORDMARK_VIEWBOX.y} ${WORDMARK_VIEWBOX.width} ${WORDMARK_VIEWBOX.height}`} aria-hidden="true" focusable="false">
            <defs>
              <linearGradient id={reflectionFadeId} x1="0" y1="174" x2="0" y2="214" gradientUnits="userSpaceOnUse">
                <stop offset="0" stopColor="white" stopOpacity="0.22" />
                <stop offset="0.55" stopColor="white" stopOpacity="0.06" />
                <stop offset="1" stopColor="white" stopOpacity="0" />
              </linearGradient>
              <mask id={reflectionMaskId} maskUnits="userSpaceOnUse" x="-10" y="172" width="708" height="44">
                <rect x="-10" y="172" width="708" height="44" fill={`url(#${reflectionFadeId})`} />
              </mask>
              <filter id={reflectionBlurId} filterUnits="userSpaceOnUse" x="-10" y="172" width="708" height="46">
                <feGaussianBlur stdDeviation="0.7 1.4" />
              </filter>
              <linearGradient id={horizonId} gradientUnits="userSpaceOnUse" x1="30" y1="170" x2="658" y2="170">
                <stop offset="0" stopColor="#d9e3f1" stopOpacity="0" />
                <stop offset="0.5" stopColor="#e6edf8" stopOpacity="0.65" />
                <stop offset="1" stopColor="#d9e3f1" stopOpacity="0" />
              </linearGradient>
            </defs>
            <g id={wordmarkLettersId} fill="none" stroke="currentColor" strokeWidth={WORDMARK_STROKE} strokeLinecap="round" strokeLinejoin="round">
              {WORDMARK_LETTERS.map(letter => (
                <path key={letter.x} d={letter.path} transform={`translate(${letter.x} 0)`} />
              ))}
            </g>
            <line className="aura-horizon" x1="30" y1="170" x2="658" y2="170" stroke={`url(#${horizonId})`} strokeWidth="0.8" />
            <g mask={`url(#${reflectionMaskId})`} filter={`url(#${reflectionBlurId})`}>
              <use href={`#${wordmarkLettersId}`} transform="translate(0 213) scale(1 -0.22)" />
            </g>
          </svg>
        </h1>
        <div className="dots" aria-hidden="true"><span /><span /><span /></div>
        <p>ADAPTIVE USER-AWARE REASONING ASSISTANT</p>
      </section>

      <section className="talk-area" aria-label="Talk to Aura">
        <form className="talk-bar" onSubmit={(event) => {
          event.preventDefault()
          if (message.trim()) {
            console.log('Message:', message)
            setMessage('')
          }
        }}>
          <span className="talk-border-trace" aria-hidden="true">
            <svg focusable="false">
              <rect className="border-trace-soft" x="1" y="1" rx="31" pathLength="100" />
              <rect className="border-trace-core" x="1" y="1" rx="31" pathLength="100" />
            </svg>
          </span>
          <span className="spark"><Icon name="spark" /></span>
          <input aria-label="Message Aura" value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Ask anything..." autoComplete="off" />
          <button className="submit-button" type="submit" aria-label="Submit message" title="Submit message">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M12 19V5m-6 6 6-6 6 6" />
            </svg>
          </button>
        </form>
      </section>

      <nav className="bottom-nav" aria-label="Main navigation">
        {navItems.map((item, index) => (
          <button type="button" key={item} className={active === item ? 'nav-item active' : 'nav-item'} aria-pressed={active === item} onClick={() => setActive(item)}>
            <Icon name={navIcons[index]} /><span>{item}</span>
          </button>
        ))}
      </nav>
    </main>
  )
}

export default App
