// Custom stroked recreation informed by Artyway's public Futurism specimen:
// https://graphicriver.net/item/futurism-headline-font/29159636
// This is SVG lettering, not the commercial OTF font or purchased vector asset.
// Keep these paths and stroke settings shared with the shimmer sampler.
export const WORDMARK_VIEWBOX = { x: -10, y: -10, width: 708, height: 180 }
export const WORDMARK_STROKE = 5
const a = 'M0 160L66 0L110 104H64'
export const WORDMARK_LETTERS = [
  { x: 15, path: a },
  { x: 195, path: 'M0 0V100C0 180 120 180 120 100V0' },
  { x: 375, path: 'M0 0H46C142 0 142 100 46 100H10L112 160' },
  { x: 563, path: a },
] as const
