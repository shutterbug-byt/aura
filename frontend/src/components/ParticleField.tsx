import { useEffect, useRef } from 'react'
import { WORDMARK_LETTERS, WORDMARK_STROKE, WORDMARK_VIEWBOX } from './wordmarkGeometry'

const MAX_PARTICLES = 4000
const DENSITY_MULTIPLIER = 1.25 * 1.65
const TAU = Math.PI * 2

/** Decorative, bounded simulation. All coordinates and forces use CSS pixels. */
export default function ParticleField() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const context = canvas?.getContext('2d', { alpha: false })
    if (!canvas || !context) return

    const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
    const coarse = window.matchMedia('(pointer: coarse)')
    // x, y, depth, radius, opacity, phase, offsetX, offsetY, velocityX, velocityY, driftX, driftY
    const stride = 12
    const particles = new Float32Array(MAX_PARTICLES * stride)
    const glints = new Float32Array(64 * 4)
    let glintCount = 0
    const title = document.querySelector<SVGSVGElement>('.aura-wordmark')
    const letterPaths = WORDMARK_LETTERS.map(letter => new Path2D(letter.path))
    const pointer = { x: -1000, y: -1000, vx: 0, vy: 0, energy: 0, time: 0 }
    let width = 0
    let height = 0
    let count = 0
    let frame = 0
    let lastTime = 0
    let elapsed = 0
    let slowFrames = 0
    let quality = 1
    let disposed = false
    let seed = 17
    const random = () => {
      seed = (seed * 1664525 + 1013904223) >>> 0
      return seed / 4294967296
    }

    // Sample the outside of the shared SVG strokes after layout changes.
    // This offscreen mask is never composited; the visible field stays one canvas.
    function measureTitle() {
      if (!title || disposed) return
      const bounds = title.getBoundingClientRect()
      const mask = document.createElement('canvas')
      mask.width = Math.ceil(bounds.width)
      mask.height = Math.ceil(bounds.height)
      const ink = mask.getContext('2d', { willReadFrequently: true })
      if (!ink || !mask.width || !mask.height) return
      ink.scale(bounds.width / WORDMARK_VIEWBOX.width, bounds.height / WORDMARK_VIEWBOX.height)
      ink.translate(-WORDMARK_VIEWBOX.x, -WORDMARK_VIEWBOX.y)
      ink.strokeStyle = '#fff'
      ink.lineWidth = WORDMARK_STROKE
      ink.lineCap = 'round'
      ink.lineJoin = 'round'
      WORDMARK_LETTERS.forEach((letter, index) => {
        ink.save()
        ink.translate(letter.x, 0)
        ink.stroke(letterPaths[index])
        ink.restore()
      })
      const pixels = ink.getImageData(0, 0, mask.width, mask.height).data
      const edges: number[] = []
      const alpha = (x: number, y: number) => pixels[(y * mask.width + x) * 4 + 3]
      for (let y = 5; y < mask.height - 5; y += 3) {
        for (let x = 5; x < mask.width - 5; x += 3) {
          if (alpha(x, y) === 0 && (alpha(x - 4, y) > 180 || alpha(x + 4, y) > 180 || alpha(x, y - 4) > 180 || alpha(x, y + 4) > 180)) {
            edges.push(x, y)
          }
        }
      }
      glintCount = Math.min(width < 600 ? 20 : 48, edges.length / 2)
      for (let n = 0; n < glintCount; n++) {
        const edge = Math.floor(random() * edges.length / 2) * 2
        glints[n * 4] = bounds.left + edges[edge]
        glints[n * 4 + 1] = bounds.top + edges[edge + 1]
        glints[n * 4 + 2] = random() * TAU
        glints[n * 4 + 3] = 0.4 + random() * 0.4
      }
      if (motion.matches) draw(0)
    }

    function resize() {
      if (!canvas || !context) return
      width = window.innerWidth
      height = window.innerHeight
      const constrained = coarse.matches || (navigator.hardwareConcurrency || 4) <= 4
      const dpr = Math.min(window.devicePixelRatio || 1, constrained ? 1.5 : 2,
        Math.sqrt(8_000_000 / (width * height)))
      canvas.width = Math.round(width * dpr)
      canvas.height = Math.round(height * dpr)
      context.setTransform(dpr, 0, 0, dpr, 0, 0)
      count = Math.min((constrained ? 2600 : MAX_PARTICLES) - 64, Math.max(260, Math.round(width * height * DENSITY_MULTIPLIER / (constrained ? 1700 : 1150))))
      seed = 17
      for (let n = 0; n < count; n++) {
        const i = n * stride
        particles[i] = random() * width
        particles[i + 1] = random() * height
        particles[i + 2] = Math.floor(random() * 3) / 2
        particles[i + 3] = 0.25 + Math.pow(random(), 3) * 0.85
        particles[i + 4] = 0.1 + Math.pow(random(), 2) * 0.5
        particles[i + 5] = random() * TAU
        particles.fill(0, i + 6, i + 10)
        const angle = random() * TAU
        const speed = 1.8 + particles[i + 2] * 4 + random() * 2
        particles[i + 10] = Math.cos(angle) * speed
        particles[i + 11] = Math.sin(angle) * speed
      }
      measureTitle()
      draw(0)
    }

    function draw(dt: number) {
      if (!context) return
      context.fillStyle = '#050505'
      context.fillRect(0, 0, width, height)
      context.fillStyle = '#e4e7eb'
      const moving = !motion.matches
      const decay = Math.exp(-dt * 1.7)
      pointer.energy *= decay
      pointer.vx *= decay
      pointer.vy *= decay
      const budget = Math.floor(count * quality)
      for (let n = 0; n < budget; n++) {
        const i = n * stride
        const depth = particles[i + 2]
        const phase = particles[i + 5]
        if (moving) {
          // Wrap beyond the viewport so the re-entry is never visible.
          particles[i] = ((particles[i] + particles[i + 10] * dt + 40) % (width + 80) + width + 80) % (width + 80) - 40
          particles[i + 1] = ((particles[i + 1] + particles[i + 11] * dt + 40) % (height + 80) + height + 80) % (height + 80) - 40
        }
        const x = particles[i]
        const y = particles[i + 1]
        if (moving && dt > 0) {
          const dx = x + particles[i + 6] - pointer.x
          const dy = y + particles[i + 7] - pointer.y
          const distance = Math.sqrt(dx * dx + dy * dy)
          const influence = Math.max(0, 1 - distance / 200) ** 2 * pointer.energy
          const force = influence * (0.5 + depth * 0.5)
          const inverse = 1 / Math.max(distance, 12)
          particles[i + 8] += (dx * inverse * force * 1100 + pointer.vx * force * 1.2 - particles[i + 6] * 5) * dt
          particles[i + 9] += (dy * inverse * force * 1100 + pointer.vy * force * 1.2 - particles[i + 7] * 5) * dt
          const damping = Math.exp(-4.5 * dt)
          particles[i + 8] *= damping
          particles[i + 9] *= damping
          particles[i + 6] += particles[i + 8] * dt
          particles[i + 7] += particles[i + 9] * dt
        }
        const centerX = (x - width / 2) / Math.max(width * 0.32, 1)
        const centerY = (y - height * 0.43) / Math.max(height * 0.18, 1)
        const center = Math.exp(-(centerX * centerX + centerY * centerY) * 2)
        // Quiet the lettering's backdrop, with a very faint surrounding light presence.
        const shimmer = moving ? 0.85 + Math.sin(elapsed * (0.35 + depth * 0.13) + phase) * 0.15 : 1
        context.globalAlpha = particles[i + 4] * (1 - center * 0.38) * shimmer
        context.beginPath()
        context.arc(x + (moving ? particles[i + 6] : 0), y + (moving ? particles[i + 7] : 0), particles[i + 3], 0, TAU)
        context.fill()
      }
      // Tiny edge lights share the background's slow tempo and stay behind the text.
      for (let n = 0; n < glintCount; n++) {
        const i = n * 4
        const phase = glints[i + 2]
        const time = moving ? elapsed : 0
        const shimmer = (0.5 + 0.5 * Math.sin(time * (0.45 + n % 3 * 0.07) + phase)) ** 3
        const x = glints[i] + Math.sin(time * 0.22 + phase) * 1.5
        const y = glints[i + 1] + Math.cos(time * 0.18 + phase) * 1.5
        context.globalAlpha = 0.08 + shimmer * 0.3
        context.beginPath()
        context.arc(x, y, glints[i + 3], 0, TAU)
        context.fill()
        if (n % 13 === 0) {
          context.globalAlpha = shimmer * 0.1
          context.fillRect(x - 2.5, y - 0.35, 5, 0.7)
          context.fillRect(x - 0.35, y - 2.5, 0.7, 5)
        }
      }
      context.globalAlpha = 1
    }

    function tick(now: number) {
      frame = 0
      if (disposed || document.hidden || motion.matches) return
      const raw = lastTime ? (now - lastTime) / 1000 : 1 / 60
      // Limit painting to ~60Hz even on high-refresh displays.
      if (raw < 1 / 65) {
        frame = requestAnimationFrame(tick)
        return
      }
      lastTime = now
      const dt = Math.min(raw, 0.033)
      elapsed += dt
      slowFrames = raw > 0.025 ? slowFrames + 1 : Math.max(0, slowFrames - 1)
      if (slowFrames > 150 && quality > 0.55) {
        quality = Math.max(0.55, quality - 0.15)
        slowFrames = 0
      }
      draw(dt)
      frame = requestAnimationFrame(tick)
    }

    function syncMotion() {
      cancelAnimationFrame(frame)
      frame = 0
      lastTime = 0
      pointer.energy = 0
      if (!document.hidden) {
        draw(0)
        if (!motion.matches) frame = requestAnimationFrame(tick)
      }
    }

    function onPointer(event: PointerEvent) {
      if (event.pointerType === 'touch' || motion.matches) return
      const now = event.timeStamp
      const dt = Math.max((now - pointer.time) / 1000, 0.016)
      if (pointer.time && now - pointer.time < 150) {
        pointer.vx = Math.max(-500, Math.min(500, (event.clientX - pointer.x) / dt))
        pointer.vy = Math.max(-500, Math.min(500, (event.clientY - pointer.y) / dt))
      }
      pointer.x = event.clientX
      pointer.y = event.clientY
      pointer.time = now
      pointer.energy = 1
    }
    function leave() { pointer.energy = 0; pointer.time = 0 }

    resize()
    syncMotion()
    const observer = new ResizeObserver(measureTitle)
    if (title) observer.observe(title)
    window.addEventListener('scroll', measureTitle, { passive: true })
    window.addEventListener('resize', resize)
    window.addEventListener('pointermove', onPointer, { passive: true })
    document.documentElement.addEventListener('pointerleave', leave)
    window.addEventListener('blur', leave)
    document.addEventListener('visibilitychange', syncMotion)
    motion.addEventListener('change', syncMotion)
    coarse.addEventListener('change', resize)
    return () => {
      disposed = true
      observer.disconnect()
      window.removeEventListener('scroll', measureTitle)
      cancelAnimationFrame(frame)
      window.removeEventListener('resize', resize)
      window.removeEventListener('pointermove', onPointer)
      document.documentElement.removeEventListener('pointerleave', leave)
      window.removeEventListener('blur', leave)
      document.removeEventListener('visibilitychange', syncMotion)
      motion.removeEventListener('change', syncMotion)
      coarse.removeEventListener('change', resize)
    }
  }, [])

  return <canvas ref={canvasRef} className="particle-field" aria-hidden="true" />
}
