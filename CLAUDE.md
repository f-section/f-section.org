# CLAUDE.md — f-section.org

## What this project is
The website for the F Section group of the REC Trichy (NIT Trichy) Class of 1996. It has photo and video albums organised by era (1992–96, 2016 20th reunion, 2026 30th reunion), and an archive plus yearly releases of our college magazine, Arivu Malar. The site is bilingual: English at `/`, Tamil at `/ta/`.

**Before any work, read `docs/DESIGN.md` in full.** It holds every design decision. Items marked **Open** are not settled: ask Saran before building anything that depends on them.

## Stack
- Astro (static output) and Tailwind CSS. Alpine.js only for small interactive parts.
- Hosting: Cloudflare Pages, built from GitHub (`main` = production, `staging` = preview).
- Media: Cloudflare R2 bucket `f-section-media`, served at `media.f-section.org`.
- Ingest script: Python, in `scripts/ingest/`.

## Commands
(Fill these in during Phase 0.)
- Dev server: `npm run dev`
- Build: `npm run build`
- Content check: `npm run check`
- Ingest (dry run is the default): `python scripts/ingest --album <slug> --src <path>`

## Rules (must follow)
1. **Never commit photos, videos, audio or scans to git.** Media goes to R2 through the ingest script. Only icons and fonts may live in `public/`.
2. **Never push to `main`.** Work on `staging` or a feature branch. Saran merges after checking the preview.
3. **Never delete or overwrite anything in R2** without listing the exact objects and getting Saran's explicit "yes". Upload with `rclone copy`, never `rclone sync`.
4. **Do not create, change or delete Cloudflare resources** (Pages projects, buckets, DNS, Access policies) without asking first.
5. **Bilingual:** every interface string goes in both `src/i18n/en.json` and `src/i18n/ta.json`. Missing Tamil content falls back to English. Never invent Tamil translations. Leave them empty for Saran.
6. **Privacy:** strip GPS data from all media. Members-only content stays under the `members/` prefix. In Memoriam entries need `family_consent: true`, or the build fails. No phone numbers or addresses anywhere.
7. **Readers are mostly 50+ and on phones:** 18 px base text, high contrast, tap targets of at least 44 px, light pages, and OpenGraph previews on every page.
8. **Budget:** free tiers only. Warn Saran if R2 storage approaches 8 GB, or if a change would add a paid service.
9. **For a non-trivial task,** show a short plan first and wait for approval.

## When a decision changes
Update `docs/DESIGN.md` and add a dated note in `docs/decisions/`. Do not change a decision without Saran's approval.
