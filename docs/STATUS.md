# STATUS: f-section.org

Where the project stands, and what comes next. Update this file at the end of every working session. No private links, tokens or personal details: this repo is public.

_Last updated: 2026-11-02, after the second read of Arivu Malar on the web_

## Live
- https://f-section.org (English) and https://f-section.org/ta/ (Tamil). Served by the Cloudflare Worker `f-section-site`, which deploys from `main` through Workers Builds.
- Staging preview: https://staging-f-section-site.asaravanan75.workers.dev
- Media: R2 bucket `f-section-media`, served at https://media.f-section.org. About 196.8 MiB of the 10 GB free tier across 237 objects: the link-preview image, two videos with posters, the first two 30th reunion albums, and Arivu Malar 2026 (71 pictures and the printed book, uploaded 2026-10-31). Twenty-four of those objects are no longer referenced — three photos dropped from Arivu Malar on 2026-10-30, three thumbnails they belonged to, the seventeen 1200px `அன்று` scans the thumbnails replaced, and மோகன் சுகுமார்'s first thumbnail, replaced on 2026-11-02 by his crop from the printed book; nothing is deleted from R2 without Saran's explicit yes.
- Pages: Home, About, Gallery (by era, with the first two real 30th reunion albums), Videos, Reunions, Arivu Malar.
- minnaham has a headless Chromium since 2026-11-01, for looking at a built page rather than reading
  its HTML: Playwright in `/mnt/data/f-section/tools/browser/` (outside the repo, so it adds no
  dependency to it), with `shot.mjs <out-dir> <width> <path>…` for full-page screenshots of the
  preview. It scrolls each page before capturing, or `loading="lazy"` pictures come out blank.
- Two videos on Videos, Reunions and Gallery → 2026: the montage ("30 years on: Reunion 2026", 4:28)
  and the kavithai (1:36). Both are live since the 2026-11-01 merge.
- **Arivu Malar 2026, the web edition**: `/arivumalar/`, the issue page, 27 reading pages, the
  `அன்றும் இன்றும்` index and 19 `noindex` profile pages, in both languages, plus the printed book
  as a 39.5 MB PDF. Live since 2026-11-01 (PR #10).

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

### Done on 2026-10-26
8. **First two albums ingested and live in R2.** `2026-reunion-campus` (31 photos, opening on the
   main gate, then the five department groups, then the afternoon in time order) and
   `2026-reunion-arivu-malar` (32, including all 16 people who spoke). 63 originals totalling
   395 MB became 126 web files totalling 13 MB. Originals are in
   `/mnt/data/f-section/originals/<slug>/<contributor>/`.
   Two bugs in `scripts/ingest` were found by running it on real files for the first time, both
   fixed with regression tests:
   - **GPS with no fix became `NaN`.** A camera that writes GPS tags without a fix leaves 0/0
     rationals, and `float(IFDRational(0, 0))` is `nan`, not an error. It passed the "is it 0,0"
     check (`nan == 0` is False), reached `media.json` as bare `NaN`, and broke the build, because
     that is not valid JSON. Now dropped, with a range check as well.
   - **`write_manifest` re-sorted by id on every run**, which would have silently undone the
     campus album's deliberate order the next time anything was ingested into it. It now keeps the
     order of whatever is already in the manifest and appends new items after it.

### Paused 2026-10-26, mid-review
Albums 3 and 4 are **chosen but not ingested**. Saran is reviewing the contact sheets.
- `2026-reunion-outings` — 19 of 74 (Vayalur, Mukkombu, Banana Leaf, Rockfort, Main Guard Gate)
- `2026-reunion-hotel` — 22 of 127 (train up, check-in, Ammikal lunch, pool, swings, train home)
- The 128 undated WhatsApp files: **recommend taking none.** 95 are under 2 MP; the 28 usable
  distinct moments are the Mukkombu walkway and the lit Rockfort, both already covered by better
  cameras.

The pick lists, the reasoning and how to resume are in
`/mnt/data/f-section/work/curation/PICKS-PENDING-REVIEW.md`, with the triage data and the
scripts beside it. Contact sheets are in `/mnt/data/f-section/review/`. None of that is in git:
it names contributors and is working material, not site content.

Running total if approved: 94 photos of 563 across four albums.

### Done on 2026-10-30
9. **Arivu Malar album reworked** on Saran's notes after seeing it live, and **the gallery and
   the video player learned to navigate** (`docs/decisions/2026-10-30-lightbox-and-video-restart.md`).
   - Cover is now `IMG_8847` (the group of seven, just after the release). The old cover,
     `IMG_8843`, was already inside the album and stays there.
   - `IMG_8867` added: the one woman who came to the event, speaking.
   - Out: `IMG_8887`, `IMG_8908` and `IMG_8837` (all repeats of a face already in the album;
     `IMG_8837` and `IMG_8840` are both Saran speaking, so only `IMG_8840` stays).
     In: `IMG_8836`, `IMG_8845`, `IMG_8864`, `IMG_8900`, `IMG_8902`, `IMG_8936`.
     All from `07 - Mohanraj/1st Cut`. **32 → 36 photos.**
   - Order reworked so the same face is not in two frames running. The one place it still is,
     deliberately, is 9–11 (`IMG_8843` → `IMG_8845` → `IMG_8847`): that is the release itself,
     told in three frames, and the same handful of people are in all of them.
   - New ids continue the sequence (`_033`–`_039`), so nothing already in R2 was renamed.
     Contact sheet of the new order: `/mnt/data/f-section/review/arivu-malar-v2.jpg`.
   - **Lightbox** (`src/components/Lightbox.astro`): tapping a photo now opens it in place with
     first · back · forward, a counter, swipe, arrow keys and Escape. It layers on the existing
     photo links, so with no JavaScript the album behaves exactly as before.
   - **Videos**: a "Start from the beginning" button under each one.
   - Six new interface strings. **The Tamil is Claude's draft and needs Saran's eye.**

### Done on 2026-10-31
10. **Arivu Malar 2026 e-book — checkpoint 1, the text is in.** Pulled the whole magazine out of
   the Claude Design export (`/mnt/data/f-section/arivumalar/2026/incoming/claude-design-arivumalar-source/`)
   and into repo content. **28 reading pages, 19 profile pages, about 5,000 words of Tamil,
   69 photographs listed.** The export's `.dc.html` files carry the Tamil live in the markup, so
   there was no OCR, no `.docx` pass and no retyping: every string is copied byte for byte.
   `scripts/arivumalar/extract.py --verify` re-reads the export and reports **no text lost**.
   - Saran's decisions on 2026-10-30/31 cut the plan from three modes to two (read online + the
     39.5 MB PDF, no page-image book view), put the e-book in the **site's own look** rather than
     the book's, made the profile pages `noindex`, and set **first names only** (rule 14) with the
     printed name kept in each file. See `docs/decisions/2026-10-31-arivumalar-ebook-shape.md`.
   - The reading order is the **printed** order for now; Saran reorders after reading it on the
     web. It lives as one `order:` list in `src/content/arivumalar/2026.yaml`.
   - `கவிதைகள்` is split into eight poem pages scattered through the book, as Saran asked. There
     turned out to be **five** குமாரவேல் poems, not four: `மூச்சுவிடும் தூரம்` was tucked onto the
     spot-the-difference answers page as filler, and now has its own page.
   - New collections `arivumalarSections` and `arivumalarPeople`, plus a `taPair` type (Tamil
     required, English optional) in `src/content.config.ts`. `npm run check` and `npm run build`
     are clean.
   - Review document for Saran: `/mnt/data/f-section/review/arivumalar-extract-2026-10-31.md`.
   - Names settled the same day: **இரமேஷ் கண்ணன்** and **மோகன் சுகுமார்** are two-word first
     names, not name plus surname; இஸ்மாயில் and சுகந்தி stay as they were. The two short poems
     printed inside குமாரவேல்'s profile (they filled the leftover half page in print) are now
     scattered pages of their own. Alt text stays **empty** where
     the print design had none, by Saran's call: the pages emit `alt=""`, the correct mark for a
     decorative picture.
   - `scripts/arivumalar/proof.py` renders the whole magazine as one HTML sheet at the site's
     18px Noto Sans Tamil for proofreading: `/mnt/data/f-section/review/arivumalar-proof.html`.
   - Still open: the `அன்று` photos of வைரமுத்து and ஸ்ரீதர் plus மோகன் சுகுமார்'s `இன்று` photo,
     all three to be cropped from the printed book. கான்ஸ்டன்'s four essay photographs were held
     open for captions and are now settled: none, as the design had them (Saran, 2026-10-31).

11. **Arivu Malar 2026 e-book — checkpoints 2 and 3, the proofread and the pages.** Saran read the
   proof sheet and sent three corrections, all applied: குமாரவேல்'s two short poems now share one
   page (`நிழல்கள் · நீயிருக்கும் வகுப்பறை`); the `மூச்சுவிடும் தூரம்` provenance line is right as
   it stands, because that poem really was printed on the spot-the-difference answers page as
   filler; and each profile can now carry a third photograph of them speaking on release night.
   - **The e-book is built: 96 pages.** `/arivumalar/` with a card per issue, `/arivumalar/2026/`
     (cover, contents, **முகப்பு**, **தரவிறக்கம் · 39.5 MB**), 27 reading pages, the
     `அன்றும் இன்றும்` index and 19 `noindex` profile pages — all of it in both languages.
   - The contents live behind a **பொருளடக்கம்** button at every width (a `<dialog>`, falling back
     to a link to the issue page), so the reading column has the screen to itself. Every page ends
     with prev · next. The crossword is a real CSS grid, and both puzzles keep their answers behind
     a **விடைகள்** button.
   - The third profile photograph is a **tag, not an upload**: `photo_event: { album, id }` points
     at a picture already in the `2026-reunion-arivu-malar` album, so the same object serves both
     pages. The slot is built and empty — Saran tags them from
     `/mnt/data/f-section/review/arivumalar-tagging.html`. Only `அன்று` and `இன்று` are captioned
     (Saran, 2026-10-31): two labels for the three pictures, with the album link below the row.
   - 18 new `ebook.*` interface strings in both languages; the Tamil is Claude's draft under
     rule 5 and wants Saran's eye.
   - `scripts/arivumalar/media.py` converted **71 pictures** (8.3 MB) and staged them with the
     printed book. **Uploaded on 2026-10-31** with Saran's yes: `rclone copy --immutable` put 72
     new objects / 46.0 MiB in place, overwriting nothing, and the covers, the pictures and the
     39.5 MB book all answer 200 from `media.f-section.org`. R2 is now 196.7 MiB of the 10 GB.
   - `npm run check` (0 errors), `npm run build` (122 pages) and `npm run check:links`
     (3,794 links) are all clean.
   - Still open: Saran's photo tags and the three photo crops from the printed book
     (வைரமுத்து and ஸ்ரீதர்'s `அன்று`, மோகன் சுகுமார்'s `இன்று`).

12. **Arivu Malar 2026 — the first read on the web, and seven changes** (2026-10-31, same evening).
   Saran read the preview and sent seven corrections, all applied and pushed to the open PR. They
   come down to one thing: where the web edition still behaved like a printed book, it read badly.
   - **The pictures.** `அன்று` is a thumbnail now — those are scans of a page printed 30 years ago,
     and the design export had framed them the size of a modern photograph, so they showed nothing
     but their own pixels. And nothing is cropped to a 4:5 box any more: many of the family
     pictures are wide, and the crop was cutting people off at both ends, two of them off Saran's
     own. The `அன்றும் இன்றும்` cards letterbox theirs inside the frame instead, so the grid of 19
     stays even, and they carry the person's name alone, not the city.
   - **`சொல்ல மறந்த கதை` is no longer a page.** Those closing words were a spread in print because
     the profile pages had no room left; online they do, so each one now ends its own profile page
     under that heading. `extract.py` still reads the spread — it is where the quotes come from —
     but no longer writes it as a reading page, so the book is 27 pages, not 28.
   - **The English pages print the magazine's own Tamil titles.** They had been showing the
     author's name and nothing else, because `title.en` is empty for every section and the contents
     fell back to it. Only names change language now, and the Latin spelling comes from the slug
     already in that person's URL and photo file names — nothing is transliterated here (rule 14).
     கலைச்செழியன் and மகேந்திரன் have no profile page, so no slug: their names stay Tamil until
     Saran gives a spelling.
   - **The contents sidebar is gone** at every width, and the issue page has lost the page count,
     the editor's line and the note under the download button.
   - `/arivumalar/` now carries its Tamil caption, in Saran's own words.
   - **The 1996 portraits were then rebuilt as even thumbnails** (`public/arivumalar/2026/then/`,
     320×400): the odd scanned edge trimmed, every one pulled to the same brightness and contrast,
     the print screen softened in proportion to the shrink, the same 4:5 frame. மரகதவல்லி's gains
     most — her scan still had the photograph's dark mount around it. 17 objects, 150 KB in all,
     uploaded on 2026-10-31; the 1200px originals stay in R2 unreferenced, and nothing was
     overwritten. R2 is now 196.8 MiB across 234 objects.
   - The names on the `அன்றும் இன்றும்` cards are in the site's heading face: Caveat on the English
     pages, the hand that writes "F Section" in the header, and Noto Sans Tamil on the Tamil ones.
   - **கலைச்செழியன் is `Kalaichezhian` and மகேந்திரன் is `Mahendran`** (Saran, 2026-10-31), the two
     poets with no profile page and so no slug to take a spelling from. They are in `ENGLISH_NAMES`
     in `extract.py`; every other Latin spelling comes from the person's own slug.

### Done on 2026-11-02
13. **Arivu Malar 2026 — the second read: the type, the pictures and the headings.** Saran read the
   live book and sent five more changes, all in one PR off `staging`. The through-line this time is
   that the web edition still looked like a website, not like a book.
   - **The reading column is set as a book now.** Noto Serif Tamil at 15.75px over a 38em measure,
     where it was the screen sans at 18px. The first pass stopped at 17px, reasoning from rule 7
     that readers past fifty need the larger type; Saran's answer was that age should not decide it
     — the book is not read only by the class of '96, and they read smaller type everywhere else
     all day. This one column is the site's only exception to the 18px base; everything else,
     including the issue and index pages, is untouched. One number in `global.css` moves it.
   - **A picture inside an article sits in the text**, the way a magazine sets one: its paragraph
     floats, so it takes about a third of the column and the article runs on beside it, and they
     alternate sides down the page. A standing portrait is held by its height instead of its width
     and comes out as a narrow strip. On a phone there is no room beside one, so it keeps its own
     line. A paragraph of nothing but bold text after a picture is that picture's caption — seven
     in this issue — and is set as one, under the picture.
   - **The headings follow the printed book**: the kind of piece above in small letterspaced
     capitals, the title in red with the half after a colon pushed out to the right margin, and the
     author's name under a short red rule. Tamil has no italic face, so the rule, the colour and the
     letterspacing do what the print's italic did. On the In Memoriam page, which prints on ink, the
     title takes the paper colour and the rest `rule`. The English pages now print the author's
     Latin name even where the Tamil page keeps the printed byline with its role or city.
   - **Every poem says `கவிதை`**, the way the stories say `கதை` and the articles `கட்டுரை`, then the
     issue's name. Where the print used a word that is not a kind it is kept after it, so the In
     Memoriam poem reads `கவிதை · நினைவஞ்சலி`. `kicker_for()` in `extract.py` does it, so a re-run
     of the extractor keeps it.
   - **The three 1996 portraits are in**, cropped from the printed book by Saran. வைரமுத்து and
     ஸ்ரீதர் had none at all; மோகன் சுகுமார்'s replaces the export's own scan, under a key of its
     own, so nothing in R2 was overwritten. They are 105–158px wide, so `media.py` stops the frame
     at twice the crop rather than inventing detail, and reads them as grey — a photograph of a
     printed page carries a colour cast the page never had.
   - Seen in the headless browser at 1280 and 390px, both languages, including the dark In Memoriam
     page and the three new profiles. `npm run check` (0 errors) and `npm run build` (122 pages)
     clean. See `docs/decisions/2026-11-02-arivumalar-reading-type.md`.


### Next
14. **Arivu Malar 2026 — what is left after going live.** [PR #10](https://github.com/f-section/f-section.org/pull/10)
   was merged on 2026-11-01 and the book is on f-section.org. Still to come: the reading order,
   which Saran settles after reading it through (one `order:` list in
   `src/content/arivumalar/2026.yaml`); his eye over the 18 Tamil interface strings; his
   `photo_event` tags from `/mnt/data/f-section/review/arivumalar-tagging.html`. The three photo crops arrived on 2026-11-02 and are in.
15. **Photo curation, remaining two albums** (deferred on 2026-10-30, picks already chosen and
   waiting in `/mnt/data/f-section/work/curation/PICKS-PENDING-REVIEW.md`). Contact sheets per
   event, then picks. Weighting, as Saran restated on
   2026-10-25: strongly prefer natural and candid — friends talking, walking, unaware of the
   camera — over posed shots at the lens. Posed is acceptable occasionally, not as the default.
   Start from Mohanraj's `1st Cut` (208 Canon frames, the backbone).
16. **Two montages, by day** (deferred on 2026-10-30; Saran changed this on 2026-10-26, replacing the three themed ones
   agreed the day before): **Day 1** and **Day 2**. Reason: each day mixes campus, temple, meals
   and evening material, so a day-shaped cut varies the imagery, where a theme-shaped cut would
   string together many near-identical scenes. Day 3 is only departure and tails Day 2.
   Music: `masters/Nanban-En_Frienda_Pola.mp3` (3:53), a different section under each montage.
   It is a loud master (-10.6 LUFS, +0.6 dBTP) and must be normalised down for web.
17. **Review page.** Contact sheet in `review/` for approval before any ingest.
18. **Ingest and upload.** R2 token and `r2` remote are in place since 2026-10-26.
19. **Open a PR** from `staging` with the album pages and the video entries.

### Notes worth keeping
- The kavithai source plays **mirrored** (a `-180` display matrix plus a selfie-camera mirror);
  it needs `hflip` on top of autorotation. Four other clips carry rotation flags and must each be
  checked the same way before use.
- Drive is live, not frozen: one file was renamed during this session, between the metadata
  snapshot and the download. Re-snapshot before trusting an older listing.

## Open items
- GPS coordinates stay in `media.json` although nothing displays them any more. Droppable if that
  ever bothers Saran; they are also in `originals/<album>/manifest.csv`, outside git.
- O-7: footer and takedown notice. Saran leans towards neither.
- Second admin for GitHub, Cloudflare and the domain (RUNBOOK).
- Tamil intro text for the pages (Saran writes it).
- Copy the montage masters and the song from the Windows laptop to `/mnt/data/f-section/masters/` on minnaham.
- The Windows fallback's `scripts/ingest/.venv` predates `pillow-heif` becoming a hard
  requirement. Re-run the install there if that machine is ever used again.
