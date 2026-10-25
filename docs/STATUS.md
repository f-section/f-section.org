# STATUS: f-section.org

Where the project stands, and what comes next. Update this file at the end of every working session. No private links, tokens or personal details: this repo is public.

_Last updated: 2026-10-25_

## Live
- https://f-section.org (English) and https://f-section.org/ta/ (Tamil). Served by the Cloudflare Worker `f-section-site`, which deploys from `main` through Workers Builds.
- Staging preview: https://staging-f-section-site.asaravanan75.workers.dev
- Media: R2 bucket `f-section-media`, served at https://media.f-section.org. About 98.5 MiB is used: the link-preview image, and the 30th reunion montage with its poster.
- Pages: Home, About, Gallery (by era, with a sample album that uses placeholders), Videos, Reunions, Arivu Malar.
- The 30th reunion montage ("30 years on: Reunion 2026", 4:28) is live on Videos, Reunions and Gallery → 2026.

## Done (PRs 1–5, all merged)
1. Site scaffold: bilingual routing, fonts, sepia theme, checks, CI, branch protection.
2. Cloudflare: Worker, custom domains, R2 bucket and media domain.
3. Tamil interface text. The logo, tagline and footer stay in English.
4. Montage: new title cards, end card, and the song completed under the end card.
5. One 1080p file per video (CRF 22), uploaded to R2.

## Next task: the 30th reunion gallery from Google Drive
Rules: `docs/decisions/2026-10-25-gallery-import-and-curation.md`. Machine: minnaham (`docs/decisions/2026-10-25-build-on-minnaham.md`).

1. **Set up minnaham.**
   - Clone the repo, run `npm install`, and run `git config core.hooksPath .githooks`.
   - Create the Python venv for `scripts/ingest`, and make sure `npm run check` and the ingest tests pass.
   - Saran creates a new R2 token for an `r2` rclone remote.
2. **Drive access.** Set up a read-only rclone remote limited to the reunion photo folder. Saran gives the folder IDs in chat; they are kept in `~/.config/`, never in the repo.
3. **Inventory.** List every contributor folder: file counts, sizes, photos vs videos, and how many files have EXIF dates and GPS.
4. **Download** everything to a staging folder on minnaham. Copy the originals to the NAS under `f-section/originals/2026-30th/`.
5. **Clean up:**
   - Remove exact duplicates, keeping the copy with the best metadata.
   - Convert HEIC photos and HEVC videos.
   - Fill in dates from file names where EXIF is missing.
6. **Rename** to `<date>-<time>_<who>_<place-or-event>_<NNN>`, and write the manifest CSV that links each new name to its Drive original.
7. **Group into events** by time and GPS. Ask Saran for the reunion schedule only if the grouping is unclear.
8. **First-pass curation:**
   - Pick the few best photos per event, preferring candid, natural shots. Start from Mohanraj's folder.
   - Pick a handful of videos.
9. **Review page.** Build a contact sheet (not published) where Saran approves the picks and the album names.
10. **Ingest** the approved picks into albums. Upload to R2 and check the bucket size.
11. **Open a PR** from `staging` with the album pages. Saran merges it.

## Open items
- O-7: footer and takedown notice. Saran leans towards neither.
- Second admin for GitHub, Cloudflare and the domain (RUNBOOK).
- Tamil intro text for the pages (Saran writes it).
- Remove the placeholder sample album once real albums are in.
- Copy the montage masters and the song from the Windows laptop to the NAS.
