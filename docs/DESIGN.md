# f-section.org — Design Decisions

| | |
|---|---|
| **Version** | 0.2 |
| **Date** | 2026-10-12 |
| **Owner** | Saran (sole maintainer for now) |
| **Repo** | `github.com/f-section/f-section.org` (private) |
| **Master copy** | `docs/DESIGN.md` in the repo is the master copy. Change it by pull request, not in chat. |

---

## 0. How to read this document

This document records what we decided for the f-section.org website and why. It is written for two readers:

1. **Saran**, who owns the site and makes the final calls.
2. **Claude Code**, which will write the code. Claude Code should read this whole document before starting any work. The root `CLAUDE.md` file points here.

Each decision is marked with a status:

- **Decided**: build it this way unless Saran changes it.
- **Open**: not settled yet. Do not build anything that depends on it. Ask Saran first.

When a decision changes, update this file and add a short note in `docs/decisions/` (one file per decision: what changed, why, and the date).

---

## 1. Purpose and audience

### 1.1 Purpose

f-section.org is a home on the web for the F Section group of the REC Trichy (now NIT Trichy) Class of 1996, batch 1992–96. It has three jobs:

1. Keep our memories (photos, videos and audio) from college days, the 20-year reunion (2016) and the 30-year reunion (2026) in one well-organised place.
2. Publish our college magazine **Arivu Malar** (அறிவு மலர்): an archive of the old hand-written issues from 1992–96, plus a new issue every year starting with the 2026 30th-anniversary special.
3. Give the group a place to keep growing: events, stories, milestones, and remembering friends we have lost.

### 1.2 Who will use the site

| Group | Notes |
|---|---|
| F Section classmates | The core group. A small subset of the batch. |
| The wider 1992–96 batch | Classmates from other sections. |
| Spouses, children, family and friends | Welcome as viewers. |
| **Total** | **Design for at most 500 unique users.** |

### 1.3 What this audience means for the design

- **Most readers are in their 50s.** Use large text (18 px base), strong contrast, big tap targets and simple navigation. Do not hide important things behind small icons.
- **Most people will open the site on a phone, from a link shared on WhatsApp.** Every page and album needs a good link preview: an OpenGraph title, description and image.
- **Many readers are in India on mobile data.** Pages must be light. Images load lazily and come in the right size for the screen.

### 1.4 Constraints

- **Budget:** use free tiers. A few dollars a month for R2 storage is acceptable if needed. Keep total media under the storage budget in Section 9.
- **People:** Saran is the only maintainer for now. Friends send content through Google Drive. Saran curates it and uploads it. Direct uploads by members may come later (Phase 4).

---

## 2. Decision summary

| ID | Decision | Status |
|---|---|---|
| D-01 | The repo is named `f-section/f-section.org`, matching the domain. | Decided |
| D-02 | The site is built with **Astro** (static output) and **Tailwind CSS**. | Decided (see note) |
| D-03 | The site is hosted on **Cloudflare Pages**, connected to the GitHub repo. | Decided |
| D-04 | Photos, videos, audio and scans are stored in **Cloudflare R2** and **never committed to git**. | Decided |
| D-05 | The site is **bilingual (English and Tamil)** with a language toggle at the top, as on ief-global.org. English is the default. | Decided |
| D-06 | **Mixed visibility.** The first pages are public. Personal content goes behind a login later. | Decided |
| D-07 | Login has two stages: 2a uses Cloudflare Access (at most 50 users); 2b uses our own login for up to 500 users. | **Open (O-1)** |
| D-08 | Videos are MP4 files in R2. We do not use YouTube, because the total footage is under 30 minutes. | Decided |
| D-09 | Work goes to a `staging` branch first. `main` is production. Nothing goes live without a preview. | Decided |
| D-10 | The site asks search engines not to index it (`noindex`) until the group decides otherwise. | **Open (O-2)**, safe default |
| D-11 | Original full-size files stay on the NAS and in Google Drive. R2 holds only web-sized copies. | Decided |
| D-12 | Media is vetted by hand before ingest; the site keeps GPS location and runs no consent checks of its own (Section 13). | Decided (changed 2026-10-12) |
| D-14 | **Public-first.** Build a simple public site now. Logins and members-only areas (Phase 2, O-1) are deferred to a much later version. | Decided (2026-10-12) |
| D-13 | The In Memoriam section is members-only by default, and nothing goes up without the family's consent. | Decided |

**Note on D-02.** ief-global.org uses HTML, Tailwind, Alpine.js and a Python build script. That approach would also work here. We chose Astro for this site for three reasons:

- It has **content collections with schema checks**, so a mistake in an album file stops the build instead of breaking a page.
- It has **built-in support for multilingual URLs**.
- It handles **hundreds of albums** more easily than a hand-written build script.

Alpine.js can still be used for small interactive parts. If Saran prefers to reuse the IEF pipeline, change D-02 before Phase 0 starts.

---

## 3. Site map

`[P]` means public. `[M]` means members only (behind the login).

```
f-section.org
│
├── /                         [P] Home: hero montage, "30 years on", latest albums
├── /about                    [P] Who F Section is: the 1992–96 story, then → now
│
├── /gallery                  [P] Index page: choose an era
│   ├── /gallery/1992-96      [P/M] College days (scanned old photos)
│   ├── /gallery/in-between   [M] 1996–2016: weddings, mini-meetups
│   ├── /gallery/2016-20th    [P/M] 20th reunion
│   ├── /gallery/2026-30th    [P/M] 30th reunion
│   │     ├── 2026-reunion-campus-walk
│   │     ├── 2026-reunion-main-event
│   │     └── 2026-reunion-hangout-spots
│   └── /gallery/places/<spot>[P] One campus spot across all eras (Then & Now)
│
├── /videos                   [P/M] Montages, grouped by era
├── /voices                   [M] Audio: speeches, songs, recorded memories (Phase 4)
│
├── /arivumalar               [P] What Arivu Malar was, who ran it
│   ├── /arivumalar/archive   [P/M] The hand-written 1992–96 issues
│   │     └── /arivumalar/archive/1993-08   one issue: cover, page viewer, contents
│   ├── /arivumalar/2026      [P/M] 30th anniversary special
│   └── /arivumalar/2027 …    yearly releases
│
├── /people                   [M] Then & Now directory (Phase 2)
├── /in-memoriam              [M] Friends we have lost (Phase 2, with family consent)
├── /reunions                 [P] 2016, 2026, and the next one
│
└── /ta/…                     The same pages in Tamil (see Section 5)
```

**Visibility is set per album, not per section.** For example, a campus-walk album can be public while the dinner photos of the same reunion are members-only. The `visibility` field in each album file controls this (Section 10).

---

## 4. How content is categorised

### 4.1 Eras (the first level)

Every album belongs to exactly one era. Eras are a fixed list:

| Era ID | Label (EN) | Covers |
|---|---|---|
| `1992-96` | College Days | Our four years on campus |
| `in-between` | The Years Between | 1996–2016: weddings, meetups, visits |
| `2016-20th` | 20th Reunion | The 2016 reunion |
| `2026-30th` | 30th Reunion | The 2026 reunion |
| `2027+` | After 30 | Anything later (add new eras as needed) |

### 4.2 Albums (the second level)

An album is one event or one theme within an era, such as "campus walk" or "main event".

### 4.3 Tags (across eras)

- **Places:** a fixed list of campus and Trichy spots (for example: main building, hostel, canteen). Places power the "Then & Now" pages, which show the same spot in 1994 and in 2026.
- **People:** not in Phase 1. If added later, people tags are opt-in and members-only.

### 4.4 Naming rules

The date comes first so that everything sorts in time order on its own.

| Item | Pattern | Example |
|---|---|---|
| Album slug | `YYYY-event-topic` | `2026-reunion-campus-walk` |
| Media file | `YYYYMMDD-HHMMSS_contributor_NNN.ext` | `20260912-101533_saran_014.webp` |
| Scanned old photo (no exact date) | `YYYY-00-00_scan_NNN.ext` | `1994-00-00_scan_007.webp` |
| Magazine issue | `YYYY-MM`. Use `volNN-issNN` instead if the originals carry numbers (**Open, O-4**). | `1993-08` |
| Place slug | lowercase, hyphens | `main-building` |

Use lowercase, hyphens and no spaces in every file name and slug.

---

## 5. Bilingual approach (English and Tamil)

- **URLs:** English pages live at the root (`/gallery/...`). Tamil pages live under `/ta/` (`/ta/gallery/...`). A link shared on WhatsApp then opens in the language it was shared in.
- **Language toggle:** a toggle at the top of every page, as on ief-global.org. It switches to the same page in the other language, not to the home page.
- **Interface text** (menus, buttons, labels) lives in `src/i18n/en.json` and `src/i18n/ta.json`. Every key must exist in both files.
- **Content text** (titles, captions, descriptions) is stored as a pair: `{ en: "...", ta: "..." }`.
  - If the Tamil text is missing, show the English text. Do not fail the page.
  - The build prints a list of items that still need Tamil, so Saran can fill them in later.
- **Fonts:** Noto Sans Tamil for body text in both languages (its Latin glyphs cover English), the same as ief-global.org and thamizh-ai.org. See `docs/decisions/2026-10-12-fonts-and-sepia.md`.
- **Old Arivu Malar issues** are shown exactly as written (scans). They are not translated.

---

## 6. Visual design

### 6.1 Theme: "Ink then, colour now"

Arivu Malar was hand-written, and that is the site's visual identity: paper, fountain-pen ink and handwriting for the past; clean, full-colour photography for the present.

- **1992–96 content** is shown with a warm sepia frame and paper texture.
- **2026 content** is shown in full colour on a clean background.
- The two looks meet on the **Then & Now** pages.

### 6.2 Starting design tokens

These are proposals. Check every text colour pair for WCAG AA contrast in Phase 0, and adjust if needed.

| Token | Value | Use |
|---|---|---|
| `--paper` | `#F6F1E7` | Page background |
| `--ink` | `#1E2A3A` | Body text (fountain-pen blue-black) |
| `--ink-red` | `#A23B2A` | Links and accents (red-ink editor's marks) |
| `--sepia` | `#846541` | 1992–96 frames and labels. Darkened from `#8A6A45`, which was 4.41:1 on paper, below AA. |
| `--marigold` | `#E0A100` | Decoration only. Never use it for text, because the contrast is too low. |
| Base font size | 18 px | Older readers |
| Tap target | at least 44 × 44 px | Phones |

**Typography:**

- **Body text:** Noto Sans Tamil for English and Tamil, self-hosted through Fontsource.
- **English headings:** Caveat Bold, used only for large headings and never for body text.
- **Tamil headings:** Noto Sans Tamil SemiBold (decided 2026-10-12, closes O-8).

### 6.3 Key components

| Component | What it does |
|---|---|
| Album card | A Polaroid-style cover photo with the title and a handwritten date |
| Era ribbon | A strip across the top of the gallery for choosing the era |
| Lightbox | Full-screen photo viewer with swipe, caption and credit |
| Then & Now slider | Two photos of the same spot (old and new); drag to compare |
| Magazine viewer | One page at a time with next and previous buttons, plus a PDF download. A page-flip effect is optional (Phase 3). |
| Video player | Native HTML5 `<video>` with a poster image and optional subtitles |
| Language toggle | EN / தமிழ், at the top right |

### 6.4 Accessibility

- Every photo has alt text (the English caption is used if no alt text is given).
- Every video has a poster image and, where possible, subtitles.
- The whole site can be used with a keyboard alone.
- Animations respect the reader's "reduce motion" setting.

---

## 7. Architecture

```
  Friends ──► Google Drive (shared folder per event)
                    │
                    ▼  Saran curates (Claude in the Claude app can help)
  Home NAS  ◄── originals (full size, master copy + offline backup)
                    │
                    ▼  scripts/ingest  (runs on Saran's Windows PC)
  ┌─────────────────────────────────────────────────────────┐
  │ Cloudflare                                               │
  │                                                          │
  │  R2 bucket: f-section-media                              │
  │    custom domain: media.f-section.org                    │
  │    prefixes:  public/   members/                         │
  │                                                          │
  │  Pages project: f-section-org                            │
  │    main    ──► f-section.org         (production)        │
  │    staging ──► preview URL           (protected, Saran)  │
  │                                                          │
  │  Access (Phase 2a): protects /members/* paths on both     │
  │    f-section.org and media.f-section.org                 │
  └─────────────────────────────────────────────────────────┘
                    ▲
  GitHub: f-section/f-section.org  (code + text + media manifests only)
```

**Key points:**

- **The website is fully static.** In Phase 1 there is no server code. This keeps it fast, free and hard to break.
- **R2 serves media directly** through `media.f-section.org`. R2 charges nothing for downloads.
- **Members-only media sits under the `members/` prefix.** In Phase 2a, Cloudflare Access protects that path. Access can protect specific paths on a hostname, so no server code is needed.
- **In Phase 2b, if we build our own login (O-1),** a small Pages Function checks the login cookie and streams members-only media from R2. Pages Functions count against the Workers free limit of 100,000 requests per day. This matters because every thumbnail would be one request. Section 9 explains how we limit this.

---

## 8. Media pipeline

### 8.1 Workflow

1. **Collect.** Friends upload to a shared Google Drive folder, with one folder per event.
2. **Curate.** Saran picks the photos to publish, removes duplicates and blurry shots, and notes captions. Claude in the Claude app can help with this step through the Google Drive connector.
3. **Archive the originals.** Copy the chosen originals to the NAS under `f-section/originals/<album-slug>/`. This is the master copy.
4. **Ingest.** Run `scripts/ingest` on Saran's Windows PC (NAS mapped as a drive). It does the following:
   - Reads the originals for one album.
   - **Keeps the date taken and the GPS location.** The display copy keeps its EXIF, and the coordinates are written to `media.json` for the map link. Thumbnails carry no metadata, to stay small.
   - Rotates each image the right way up, using its EXIF orientation.
   - Creates web copies (sizes in 8.2).
   - Names the files using the rule in Section 4.4.
   - Computes a SHA-256 hash of each file, so the same photo is never uploaded twice.
   - Writes or updates the album's `media.json` manifest.
   - Uploads to R2 with **`rclone copy`**. Never use `rclone sync`, because `sync` deletes files and `copy` does not.
   - Prints the bucket's total size after the upload (budget check, Section 9).
5. **Commit.** Commit the manifest and the album file to the `staging` branch.
6. **Review.** Open the staging preview and check the album on a phone.
7. **Publish.** Merge `staging` into `main`.

**Rule:** the ingest script only ever adds files. Removing media from R2 is a separate command that lists what it will delete and asks for confirmation before it deletes anything.

### 8.2 Output formats

| Media | Web copies | Notes |
|---|---|---|
| Photo | Thumbnail: 480 px long edge, WebP. Display: 2048 px long edge, WebP. | Quality around 80. AVIF is optional later. |
| Old scanned photo | Same as above | Scan masters at 600 dpi and keep them on the NAS. |
| Video | MP4 (H.264 + AAC) at 1080p (about 5 Mbps) and 720p (about 2.5 Mbps), plus a JPG poster | Use `-movflags +faststart` so playback starts before the whole file loads. Subtitles (`.vtt`, EN/TA) are optional. |
| Audio | MP3, 128 kbps | |
| Magazine scan | One WebP per page (1600 px long edge) plus one compressed PDF per issue | Scan masters (400–600 dpi PNG or TIFF) stay on the NAS. |

**Music warning:** montages with copyrighted film songs are a legal grey area, even on our own site. Prefer royalty-free music or our own recordings (for example, someone singing at the reunion).

---

## 9. Storage budget

The R2 free tier covers 10 GB of storage per month. After that, storage costs $0.015 per GB per month (Cloudflare pricing page, checked 2026-10-12). Downloads from R2 are free.

The figures below are **my estimates**, not measurements:

| Media | Assumption | Approximate size |
|---|---|---|
| Photos | 3,000 photos × (≈350 KB display + ≈40 KB thumbnail) | ≈ 1.2 GB |
| Video | 30 min at 1080p (≈1.1 GB) + 720p (≈0.6 GB) | ≈ 1.7 GB |
| Audio | A few hours at 128 kbps | ≈ 0.2 GB |
| Arivu Malar | 15 issues × ≈40 pages, plus PDFs | ≈ 0.3 GB |
| **Total** | | **≈ 3.4 GB, well under 10 GB** |

**Guardrails:**

- Never upload originals to R2. Only web copies go there.
- The ingest script warns at 8 GB.
- Workers requests (Phase 2b only): members-only images are served with `Cache-Control: private, max-age=31536000, immutable`, so a phone downloads each image only once. If daily requests come close to 100,000, the options are to upgrade to Workers Paid (I believe about $5 a month; please verify) or to keep Access in front of media.

---

## 10. Content model

The content files live in the repo under `src/content/`. Astro checks them against a schema, and the build fails if a file is wrong.

### 10.1 Album: `src/content/albums/<slug>/album.yaml`

```yaml
slug: 2026-reunion-campus-walk
era: 2026-30th                 # one of the eras in Section 4.1
date: 2026-09-12
title:    { en: "Campus walk", ta: "" }     # empty Tamil falls back to English
summary:  { en: "Walking our old paths, 30 years later.", ta: "" }
location: { en: "NIT Trichy campus", ta: "" }
visibility: public             # public | members
cover: 20260912-101533_saran_014
places: [main-building, hostel]
```

### 10.2 Media manifest: `src/content/albums/<slug>/media.json`

The ingest script generates this file. Edit captions in it, or keep captions in `captions.yaml` (the choice is left to the implementation).

```json
[
  {
    "id": "20260912-101533_saran_014",
    "type": "photo",
    "width": 2048, "height": 1365,
    "sha256": "…",
    "credit": "saran",
    "caption": { "en": "", "ta": "" },
    "place": "main-building",
    "pairWith": "1994-00-00_scan_007"
  }
]
```

`pairWith` links a new photo to an old photo of the same spot for the Then & Now slider.

### 10.3 Video: `src/content/videos/<slug>.yaml`

```yaml
slug: 2026-reunion-montage
era: 2026-30th
title: { en: "30 years on — montage", ta: "" }
visibility: public
duration: "04:32"
files: { "1080": "public/video/2026-reunion-montage-1080.mp4",
         "720":  "public/video/2026-reunion-montage-720.mp4" }
poster: public/video/2026-reunion-montage.jpg
subtitles: { en: null, ta: null }
music_cleared: true            # must be true before visibility can be public
```

### 10.4 Arivu Malar issue: `src/content/arivumalar/<issue-id>.yaml`

```yaml
id: 1993-08
kind: archive                  # archive | annual
year: 1993
title: { en: "Arivu Malar — August 1993", ta: "அறிவு மலர் — ஆகஸ்ட் 1993" }
visibility: public
pages: 38
pdf: public/arivumalar/1993-08/1993-08.pdf
contents:                      # typed table of contents, so the archive is searchable
  - { page: 1, title: "", author: "" }
editors: []
```

### 10.5 Person (Phase 2): `src/content/people/<slug>.yaml` (members only)

```yaml
slug: firstname-lastname
name: { en: "", ta: "" }
section: F                     # F, or another section of the batch
photo_1996: members/people/firstname-lastname-1996.webp
photo_2026: members/people/firstname-lastname-2026.webp
consent:
  listed: true                 # the person agreed to appear in the directory
  show_2026_photo: true
  show_bio: false
bio: { en: "", ta: "" }
```

The restored yearbook headshots made for the anniversary magazine can be used for `photo_1996`.

### 10.6 In Memoriam (Phase 2): `src/content/memoriam/<slug>.yaml`

```yaml
slug: firstname-lastname
name: { en: "", ta: "" }
years: "YYYY – YYYY"
photo: members/memoriam/firstname-lastname.webp
tribute: { en: "", ta: "" }    # written by friends, reviewed by the family
family_consent: true           # the build FAILS if this is not true
visibility: members
```

This page should be quiet: no comments, no counters and no social buttons.

---

## 11. Repo layout

```
f-section.org/
├── CLAUDE.md                  ← Claude Code reads this automatically
├── README.md                  ← how to run, build, deploy
├── docs/
│   ├── DESIGN.md              ← this file
│   ├── RUNBOOK.md             ← accounts, admins, renewals, how to roll back
│   └── decisions/             ← one short note per changed decision
├── src/
│   ├── content/               ← albums/, videos/, arivumalar/, people/, memoriam/, places.yaml
│   ├── i18n/                  ← en.json, ta.json
│   ├── components/
│   ├── layouts/
│   ├── pages/                 ← English at root, Tamil under ta/
│   └── styles/
├── functions/                 ← Phase 2b only: login middleware
├── scripts/
│   └── ingest/                ← Python: resize, read date and GPS, manifest, rclone upload
├── public/                    ← favicon and fonts only. NO photos or videos.
├── .github/workflows/
│   └── check.yml              ← build, schema check, link check, "no media in git" check
└── .gitignore                 ← blocks *.jpg *.jpeg *.png *.heic *.mp4 *.mov *.wav etc. outside public/icons
```

---

## 12. Environments, deployment and rollback

| Environment | Branch | URL | Who can see it |
|---|---|---|---|
| Local | any | `localhost` | Saran |
| Staging | `staging` | Pages preview URL (optionally `staging.f-section.org`) | Saran only. Protect it with Cloudflare Access (one seat). |
| Production | `main` | `https://f-section.org` | Everyone (public pages) |

- Cloudflare Pages builds every push automatically. Feature branches get their own preview URLs.
- **Never push straight to `main`.** Work on `staging` (or a feature branch), check the preview, then merge.
- **To roll back,** use the Pages dashboard to restore a previous deployment (one click), then `git revert` the bad commit so the code matches what is live.
- **Media rollback:** media files are never overwritten, because new versions get new names. To roll back, point the manifest back to the old file.

---

## 13. Privacy, consent and safety rules

1. **Location is kept.** Photos and videos keep their GPS data, so the site can show where each one was taken (a "Show on map" link). Changed 2026-10-12, see `docs/decisions/2026-10-12-public-first-curated-media.md`.
2. **Curated before ingest.** Saran and friends vet every photo by hand before it is added to an album. Anything handed to the ingest script is cleared for publishing as is. The site does not run its own consent checks.
3. **Children's photos:** left to the curators' judgement during vetting.
4. **Takedown.** People can ask for a photo to be removed by emailing Saran. Act on requests within a few days, without asking why. Where this notice appears (a page footer, the About page, or only in the WhatsApp group) is **Open (O-7)**. Saran leans towards no footer, because the site is for close friends and family.
5. **Search engines.** Every page carries `noindex` until the group decides otherwise (O-2).
6. **No personal contact details** (phone numbers, addresses) anywhere on the site, including the members area.
7. **In Memoriam** follows Section 10.6. Nothing goes up without the family's consent.
8. **Second admin.** Add one trusted classmate as an admin on the GitHub org, the Cloudflare account and the domain, and record this in `RUNBOOK.md`. If Saran is unavailable, the site must not be lost.
9. **Domain auto-renew** is on for f-section.org.
10. **Backups follow 3-2-1:** originals on the NAS, a second copy (an external drive kept offline), and a third copy in Google Drive. R2 is where the site's media lives; it is not a backup.

---

## 14. Roadmap

### Phase 0: Foundations
- [x] Create the repo `f-section/f-section.org` and an org profile repo `f-section/.github`.
- [x] Set up Astro, Tailwind, the bilingual routing (`/` and `/ta/`) and the language toggle.
- [x] Add the design tokens, fonts and base layout; check contrast.
- [x] Add the content schemas from Section 10, with build-time validation.
- [ ] Create the Cloudflare Pages project linked to GitHub, with `main` for production and `staging` for preview.
- [ ] Create the R2 bucket `f-section-media` with the custom domain `media.f-section.org`.
- [x] Write the ingest script (Section 8), with a dry-run mode.
- [x] Add the CI checks: build, schema, links, and no media files in git.
- [x] Write `README.md` and `RUNBOOK.md`.
- [ ] Add the second admin.
- **Exit:** an empty but working bilingual site is live on staging, and one test album goes through the full pipeline.

### Phase 1: Public launch (gallery and videos)
- [ ] Home, About and Reunions pages.
- [ ] Gallery: era index, album pages, lightbox, Places pages, Then & Now slider.
- [ ] Videos page with the reunion montage.
- [ ] OpenGraph previews for every page and album.
- **Exit:** the site is live on f-section.org with public albums only, and it has been tested on a phone over mobile data.

### Phase 2: Members area
- [ ] 2a: Cloudflare Access on `/members/*` for F Section (at most 50 users).
- [ ] Members-only albums, the People (Then & Now) directory and In Memoriam.
- [ ] 2b: login for the whole batch and families (depends on O-1).
- **Exit:** members can log in by email, and non-members cannot see members-only pages or media URLs.

### Phase 3: Arivu Malar
- [ ] Archive page and issue viewer for the 1992–96 issues found so far (10–15 expected).
- [ ] The 2026 30th-anniversary special.
- [ ] A yearly release routine: call for articles, edit, publish.

### Phase 4: Grow
- [ ] Member uploads into a holding area, with Saran approving before anything goes live.
- [ ] A 1992 → 2026 timeline page.
- [ ] Voices (audio memories).
- [ ] Events and RSVP for meetups and the next reunion.
- [ ] A milestones board (opt-in): children's graduations, books, awards.

---

## 15. Open decisions

| ID | Question | Options | Recommendation |
|---|---|---|---|
| **O-1** | How should up to 500 people log in? | **A.** Cloudflare Access only. Simple, but the free plan covers about 50 users, and above that it costs per user per month. **B.** Our own login: "Sign in with Google" plus an emailed one-time link, with an allowlist of emails in Cloudflare D1. The emailed links go through an email service such as Resend (free tier: 3,000 emails a month, 100 a day). **C.** A shared family passcode. Easy, but weak, because passcodes get forwarded on WhatsApp. | Use **A for Phase 2a** (F Section only). Move to **B** when the whole batch is invited. With B, send invites in batches, so the 100-emails-a-day limit is not hit on launch day. Use a maintained authentication library; do not hand-write the security code. |
| **O-2** | Should public pages appear in Google search? | Yes / No | **No** for now. This is easy to change later. |
| **O-3** | Should batchmates from other sections get their own "section" pages? | Yes / No / Later | **Later.** Revisit after Phase 2. |
| **O-4** | How should old Arivu Malar issues be identified? | `YYYY-MM` / `volNN-issNN` | Decide once the issues are found. Use `YYYY-MM` if they are unnumbered. |
| **O-5** | Where should In Memoriam be visible? | Members-only / public | **Members-only** unless a family asks otherwise. |
| **O-6** | When and how should members upload directly? | Phase 4 design | Keep curating through Google Drive until then. |
| **O-7** | Does the site need a footer with a takedown notice and contact email? | Footer on every page / About page only / no notice on the site | Saran leans towards **no footer**. Until decided, the layout has a minimal footer. The takedown line shows only once `TAKEDOWN_EMAIL` is set in `src/site.ts`. |
| ~~O-8~~ | Which font should Tamil headings use? | | **Closed 2026-10-12:** Noto Sans Tamil SemiBold. |

---

## 16. Working with Claude: the Claude app and Claude Code

The **GitHub repo is the single source of truth.** Both tools work through it. Neither one holds decisions on its own.

| Work | Where | Why |
|---|---|---|
| Writing code, building, testing, running `wrangler` or `rclone` | **Claude Code** on Saran's Windows PC (repo at `E:\COWORK\PROJECTS\F-SECTION\f-section.org`) | It has the shell, git, Node, Python, Cloudflare credentials and NAS access. |
| Running the ingest script on media | **Claude Code** on Saran's Windows PC | The originals are on the NAS, mapped as a drive. |
| Curating content from Google Drive: shortlisting, finding duplicates, captions | **Claude app** (this project) | It has the Google Drive connector and the `E:\F Section` folder. |
| Writing bilingual text: captions, About page, tributes, Arivu Malar articles | **Claude app** | Writing and review. The output becomes YAML or Markdown for the repo. |
| Visual design exploration and mockups | **Claude app** | Quick visual iterations before any code exists. |
| Design decisions | Discuss in either; **record them in `docs/DESIGN.md`** | Keeps both tools in step. |
| Reviewing the staging site | Either | |

**Hand-off rules:**

1. Text content made in the Claude app is saved as files in the repo format (for example, `album.yaml` captions) and committed to `staging`. Saran either copies the files over, or the Claude app session opens a pull request directly if the repo is attached to it.
2. When a decision changes in a Claude app conversation, the same conversation produces the updated `DESIGN.md` section, and it is committed to the repo.
3. Claude Code never changes a decision in this document without Saran's approval.

---

## Appendix A: Kickoff prompt for Claude Code (Phase 0)

Paste this into Claude Code after cloning the empty repo and copying in `CLAUDE.md` and `docs/DESIGN.md`:

> Read `CLAUDE.md` and `docs/DESIGN.md` fully. We are starting **Phase 0** (Section 14). First, give me a short plan listing the files you will create and the commands you will run, and wait for my approval. Then:
> 1. Set up Astro (static output) with Tailwind, bilingual routing (`/` English, `/ta/` Tamil) and the language toggle.
> 2. Add the design tokens and fonts from Section 6.
> 3. Add the content collections and schemas from Section 10, with one sample public album that uses placeholder images.
> 4. Add a `.gitignore` that blocks media files, and a CI workflow that fails if any media file is committed.
> 5. Write `scripts/ingest` in Python with a `--dry-run` flag that is on by default. It must keep the date and GPS data, resize to the sizes in Section 8.2, write `media.json`, and upload with `rclone copy` only.
> 6. Write `README.md` and a `RUNBOOK.md` skeleton.
> Work on the `staging` branch. Do not push to `main`. Do not create or delete any Cloudflare resources without asking me first.

---

## Appendix B: Facts to re-check (limits and prices change)

These were checked on 2026-10-12 unless noted otherwise. Re-check them before relying on them.

| Fact | Value used here | Source |
|---|---|---|
| R2 free tier | 10 GB-month storage; downloads free; $0.015/GB-month after that | [Cloudflare R2 pricing](https://developers.cloudflare.com/r2/pricing) |
| Pages limits (free) | 25 MiB per file; 20,000 files per site; 500 builds per month | [Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits) |
| Workers free plan | 100,000 requests/day; 10 ms CPU per request | [Workers limits](https://developers.cloudflare.com/workers/platform/limits/) |
| Cloudflare Access free plan | Up to 50 users. **Source is from 2020; verify the current terms.** | [Cloudflare blog (2020)](https://blog.cloudflare.com/teams-plans), [Access product page](https://www.cloudflare.com/en-au/products/cloudflare-access) |
| Access seat behaviour | When seats run out, new users are blocked. Inactive seats can expire automatically (1 month to 1 year). | [Seat management docs](https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/seat-management/) |
| Resend free tier | 3,000 emails/month; 100/day | [Resend pricing](https://resend.com/pricing) |
| Workers Paid price | About $5/month (**not verified here**) | Check the Cloudflare pricing page. |
| GitHub file limit | 100 MB per file (hard limit) | GitHub docs |
