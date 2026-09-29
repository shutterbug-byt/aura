import { useState } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState('')
  const [active, setActive] = useState('Home')

  const navItems = ['Home', 'Explore', 'Tools', 'Settings']

  return (
    <main className="aura-app">
    <div className="stars stars-one"></div>
    <div className="stars stars-two"></div>
    <div className="nebula nebula-one"></div>
    <div className="nebula nebula-two"></div>

    <div className="planet planet-left"></div>
    <div className="planet planet-right"></div>

    {/* Top bar */}
    <header className="topbar">
    <div className="top-actions">
    <button>♧</button>
    <button>◉</button>
    <button>⚙</button>
    </div>
    </header>

    {/* Orbit decoration */}
    <div className="orbit orbit-one"></div>
    <div className="orbit orbit-two"></div>
    <div className="orbit orbit-three"></div>

    {/* Main AURA section */}
    <section className="hero">
    <div className="hero-glow"></div>

    <h1 className="aura-title" aria-label="AURA">
    <span>A</span>
    <span>U</span>
    <span>R</span>
    <span>A</span>
    </h1>

    <div className="dots">
    <span></span>
    <span></span>
    <span></span>
    </div>

    <p>ADAPTIVE USER-AWARE REASONING ASSISTANT</p>
    </section>

    {/* Chat / voice input */}
    <section className="talk-area">
    <form
    className="talk-bar"
    onSubmit={(e) => {
      e.preventDefault()
      if (message.trim()) {
        console.log('Message:', message)
        setMessage('')
      }
    }}
    >
    <span className="spark">✦</span>

    <input
    value={message}
    onChange={(e) => setMessage(e.target.value)}
    placeholder="Talk to Aura..."
    />

    <div className="divider"></div>

    <button className="mic-button" type="button">
    ◉
    </button>
    </form>
    </section>

    {/* Navigation */}
    <nav className="bottom-nav">
    {navItems.map((item) => (
      <button
      key={item}
      className={active === item ? 'nav-item active' : 'nav-item'}
      onClick={() => setActive(item)}
      >
      <span className="nav-icon">
      {item === 'Home' && '⌂'}
      {item === 'Explore' && '✧'}
      {item === 'Tools' && '▱'}
      {item === 'Settings' && '⚙'}
      </span>

      <span>{item}</span>
      </button>
    ))}
    </nav>
    </main>
  )
}

export default App
