# f-section.org

The website of the F Section group, REC Trichy (now NIT Trichy) Class of 1996. It holds photo and video albums by era, and the archive and yearly releases of our college magazine, **Arivu Malar** (அறிவு மலர்). English pages are at `/` and Tamil pages at `/ta/`.

- Design decisions: [`docs/DESIGN.md`](docs/DESIGN.md)
- Rules for Claude Code: [`CLAUDE.md`](CLAUDE.md)
- Accounts, admins and rollback: [`docs/RUNBOOK.md`](docs/RUNBOOK.md)
- Changed decisions: [`docs/decisions/`](docs/decisions/)

## Stack
Astro (static output), Tailwind CSS and self-hosted fonts. Hosted on Cloudflare (Worker `f-section-site` with static assets, built from GitHub; see `wrangler.jsonc`). Photos and videos live in Cloudflare R2 (`media.f-section.org`), **never in git**.

## Run it locally
You need Node 22.12 or later, and Python 3.12 or later for the ingest script.

```bash
npm install
npm run dev
```

Open http://localhost:4321. The Tamil version is at http://localhost:4321/ta/.

## Before pushing
```bash
npm run check
npm run build
npm run check:links
```

`npm run check` fails if:
- an album, video, magazine, person or In Memoriam file breaks its schema
- an i18n key is missing from `en.json` or `ta.json`
- a media file is tracked in git
- a phone number appears anywhere
- a text colour fails WCAG AA

`npm run build` ends with a list of text that still needs Tamil.

## Adding an album
1. Create `src/content/albums/<slug>/album.yaml` (DESIGN.md §10.1). The slug looks like `2026-reunion-campus-walk`.
2. Put the chosen originals in `/mnt/data/f-section/originals/<slug>/` on minnaham's local disk (not the NAS), with one subfolder per contributor (for example `saran/`).
3. Set up the ingest script once:
   ```bash
   python -m venv scripts/ingest/.venv
   scripts/ingest/.venv/Scripts/python -m pip install -r scripts/ingest/requirements.txt
   ```
4. Run a dry run, which only prints the plan:
   ```bash
   scripts/ingest/.venv/Scripts/python scripts/ingest --album <slug> --src "Z:/f-section/originals/<slug>"
   ```
5. Run it for real with `--apply`. This step:
   - keeps the date and GPS location (for the map link)
   - makes 480 px and 2048 px WebP copies (videos at 1080p and 720p)
   - updates `media.json`
   - uploads with `rclone copy --immutable`, which never overwrites or deletes
6. Commit `album.yaml` and `media.json` to `staging`, then check the preview on a phone.

The ingest script needs `rclone` (configured with an `r2` remote) and, for video and audio, `ffmpeg`. All three tools, including `exiftool`, are installed on the Windows PC with winget. See RUNBOOK.md.

## Deploy
- `staging` branch: Cloudflare preview URL. All work goes here first.
- `main` branch: https://f-section.org. Saran merges after checking the preview. Nobody pushes to `main` directly.
