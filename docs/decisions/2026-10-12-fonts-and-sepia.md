# Fonts and sepia colour

**Date:** 2026-10-12
**Approved by:** Saran
**Affects:** DESIGN.md §5, §6.2

## Fonts: Noto Sans Tamil everywhere for body text
DESIGN.md first said "IBM Plex Sans for English, IBM Plex Sans Tamil for Tamil, the same as ief-global.org". In Phase 0 two problems came up:
- IBM Plex Sans Tamil is not on Google Fonts, Fontsource (npm) or IBM's `@ibm/plex` package.
- ief-global.org actually uses Noto Sans Tamil.

Saran's decision: use **Noto Sans Tamil** and drop IBM Plex Sans. It is the font used in all his Tamil site builds (ief-global.org, thamizh-ai.org).
- Body text in both languages: Noto Sans Tamil (its Latin glyphs cover English).
- English headings: Caveat Bold.
- Tamil headings: Noto Sans Tamil SemiBold. Kavivanar was tried and dropped. This closes O-8.

## Sepia darkened to #846541
The proposed `--sepia` `#8A6A45` gave 4.41:1 on the paper background, below WCAG AA (4.5:1). `#846541` gives 4.76:1 and looks almost the same. `npm run check` checks every text pair.
