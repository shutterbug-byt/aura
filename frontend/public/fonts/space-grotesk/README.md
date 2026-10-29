# Space Grotesk

Official Google Fonts Latin WOFF2, normal style. Weight 300 is used by the
AURA SVG text, reflection, and canvas shimmer sampler. The earlier 500 asset
is retained for the existing font definition. No runtime font download is needed
for the wordmark. Inter remains the existing separate UI font.

Source family: https://fonts.google.com/specimen/Space+Grotesk
CSS request: https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500&display=swap
Downloaded with a modern Chrome user agent on 2026-10-29. Only the Latin asset
from the response is included; only the weights used in these iterations are bundled.

Unmodified font URL:
https://fonts.gstatic.com/s/spacegrotesk/v22/V8mQoQDjQSkFtoMM3T6r8E7mF71Q-gOoraIAEj7aUXskPMA.woff2

SHA-256: `1b1a8131d9edf975d9decee81e2f2bf504812f7a4f498e5500f28a613e22e64c`

License: SIL Open Font License 1.1; see OFL.txt, copied from:
https://raw.githubusercontent.com/google/fonts/main/ofl/spacegrotesk/OFL.txt

Light (300), downloaded 2026-10-29:
https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300&display=swap
https://fonts.gstatic.com/s/spacegrotesk/v22/V8mQoQDjQSkFtoMM3T6r8E7mF71Q-gOoraIAEj62UXskPMA.woff2

Light SHA-256: `a5de30e3b00eec05d96c3db37b9a90e36c6ed68f1bed5b38eb3e6871ff04a145`

The light treatment uses native glyph outlines. Spacing and baseline are shared
with the shimmer sampler through src/components/wordmarkGeometry.ts. The
reflection reuses the rendered text with a vertical fade and slight blur.
