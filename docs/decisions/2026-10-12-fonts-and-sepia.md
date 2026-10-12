# Tamil body font and sepia colour

**Date:** 2026-10-12
**Affects:** DESIGN.md §5, §6.2

## Tamil body font: Noto Sans Tamil
DESIGN.md said "IBM Plex Sans Tamil, the same as ief-global.org". Two problems came up in Phase 0:
- IBM Plex Sans Tamil is not on Google Fonts, Fontsource (npm) or IBM's `@ibm/plex` package.
- ief-global.org actually uses **Noto Sans Tamil** (see `IEF/WEB/CLAUDE.md`).

So the site uses **IBM Plex Sans** for English body text and **Noto Sans Tamil** for Tamil, which matches IEF. Both are self-hosted through Fontsource.

## Tamil headings: Kavivanar, pending Saran's choice
Kavivanar does exist (Google Fonts, `@fontsource/kavivanar`). It is wired in as the Tamil heading font. The `/styleguide/` page shows it next to Noto Sans Tamil SemiBold so Saran can choose.

## Sepia darkened to #846541
The proposed `--sepia` `#8A6A45` gave 4.41:1 on the paper background, below WCAG AA (4.5:1). `#846541` gives 4.76:1 and looks almost the same. `npm run check` checks every text pair.
