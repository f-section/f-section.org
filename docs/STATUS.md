# STATUS: f-section.org

Where the project stands, and what comes next. Update this file at the end of every working session. No private links, tokens or personal details: this repo is public.

_Last updated: 2026-10-25_

## Live
- https://f-section.org (English) and https://f-section.org/ta/ (Tamil). Served by the Cloudflare Worker `f-section-site`, which deploys from `main` through Workers Builds.
- Staging preview: https://staging-f-section-site.asaravanan75.workers.dev
- Media: R2 bucket `f-section-media`, served at https://media.f-section.org. About 137.9 MiB of the 10 GB free tier: the link-preview image, the 30th reunion montage, and the kavithai video, each with a poster.
- Pages: Home, About, Gallery (by era, with a sample album that uses placeholders), Videos, Reunions, Arivu Malar.
- Two videos on Videos, Reunions and Gallery → 2026: the montage ("30 years on: Reunion 2026", 4:28)
  and the kavithai (1:36). The kavithai is in R2 and in the repo, but reaches the live site only
  once `staging` is merged to `main`.

## Done (PRs 1–5, all merged)
1. Site scaffold: bilingual routing, fonts, sepia theme, checks, CI, branch protection.
2. Cloudflare: Worker, custom domains, R2 bucket and media domain.
3. Tamil interface text. The logo, tagline and footer stay in English.
4. Montage: new title cards, end card, and the song completed under the end card.
5. One 1080p file per video (CRF 22), uploaded to R2.

## Next task: the 30th reunion gallery from Google Drive
Rules: `docs/decisions/2026-10-25-gallery-import-and-curation.md`. Machine: minnaham (`docs/decisions/2026-10-25-build-on-minnaham.md`).

### Done on 2026-10-25
1. **minnaham set up.** Repo, hooks, Node 24 via fnm, ingest venv via `uv`, ffmpeg 8.0.1,
   exiftool 13.50, rclone 1.75.2. See RUNBOOK, "Local tools (minnaham, main machine)".
2. **Drive access.** Read-only service account, Viewer on the reunion folder, `scope=drive.readonly`
   and `root_folder_id` pinned. RUNBOOK step 8. Nothing on the Drive is ever written.
3. **Inventory.** 578 files, 2.7 GiB, from 6 of 15 contributor folders (nine never uploaded).
   563 photos, 15 videos, 92 HEIC, 92 with GPS, shot 2-4 Oct. No exact duplicates: all 578 MD5s
   differ, so overlap between contributors is the same *moment*, not the same file.
4. **Downloaded** to `/mnt/data/f-section/drive/`, every size and MD5 verified against Drive.
   `originals/2026-30th/manifest.csv` holds Drive path, file ID, original name, SHA-256, EXIF time
   and GPS for all 578. `new_name` is still blank; it gets filled at rename time.
5. **Events.** Saran's itinerary (with the Day 2 correction: turf cricket cancelled, Uchi Pillaiyar
   moved up from Day 3 to 17:00 on the 3rd) places 448 files. GPS confirms it independently.
   The 130 WhatsApp files carry a date but no time and must be placed by eye.
6. **Videos qualified.** All 15 watched. Only the kavithai clears a strict standalone bar; the rest
   become montage material. Three WhatsApp videos are too low-resolution to use at all.
7. **Kavithai video built and approved** — `masters/2026-reunion-kavithai-master.mp4` and the
   1080p web copy in `out/public/video/`. **1:35.6**, 39.3 MB. Structure: Rockfort wide 3s, poem
   card 3s, recitation 73.5s (from 8.8s of the source), poem card 12s, Rockfort tight 4s. Audio is
   RNNoise (`sh` model) + loudnorm. Poster is the floodlit Rockfort, cut from the 4080x3060
   original rather than a video frame. Slug will be `2026-reunion-kavithai`.
   **Uploaded 2026-10-26** with `rclone copy --immutable` and
   `Cache-Control: public, max-age=31536000, immutable` (the convention the existing video and
   poster already use, not the shorter one in RUNBOOK step 7, which is for the OG image).
   `src/content/videos/2026-reunion-kavithai.yaml` added; it appears on Videos, Reunions and
   Gallery 2026 in both languages. **Tamil title needs Saran's eye**, especially the spelling of
   the name.

### Next
8. **Photo curation.** Contact sheets per event, then picks. Weighting, as Saran restated on
   2026-10-25: strongly prefer natural and candid — friends talking, walking, unaware of the
   camera — over posed shots at the lens. Posed is acceptable occasionally, not as the default.
   Start from Mohanraj's `1st Cut` (208 Canon frames, the backbone).
9. **Two montages, by day** (Saran changed this on 2026-10-26, replacing the three themed ones
   agreed the day before): **Day 1** and **Day 2**. Reason: each day mixes campus, temple, meals
   and evening material, so a day-shaped cut varies the imagery, where a theme-shaped cut would
   string together many near-identical scenes. Day 3 is only departure and tails Day 2.
   Music: `masters/Nanban-En_Frienda_Pola.mp3` (3:53), a different section under each montage.
   It is a loud master (-10.6 LUFS, +0.6 dBTP) and must be normalised down for web.
10. **Review page.** Contact sheet in `review/` for approval before any ingest.
11. **Ingest and upload.** Blocked on the R2 token for minnaham (RUNBOOK steps 5-6).
12. **Open a PR** from `staging` with the album pages and the video entries.

### Notes worth keeping
- The kavithai source plays **mirrored** (a `-180` display matrix plus a selfie-camera mirror);
  it needs `hflip` on top of autorotation. Four other clips carry rotation flags and must each be
  checked the same way before use.
- Drive is live, not frozen: one file was renamed during this session, between the metadata
  snapshot and the download. Re-snapshot before trusting an older listing.

## Open items
- O-7: footer and takedown notice. Saran leans towards neither.
- Second admin for GitHub, Cloudflare and the domain (RUNBOOK).
- Tamil intro text for the pages (Saran writes it).
- Remove the placeholder sample album once real albums are in.
- Copy the montage masters and the song from the Windows laptop to `/mnt/data/f-section/masters/` on minnaham.
- The Windows fallback's `scripts/ingest/.venv` predates `pillow-heif` becoming a hard
  requirement. Re-run the install there if that machine is ever used again.
