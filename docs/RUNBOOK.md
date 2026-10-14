# RUNBOOK: f-section.org

How the site is run: accounts, admins, renewals and recovery. Keep this current. **No passwords or API tokens in this file.**

## Accounts and admins

| What | Where | Primary admin | Second admin (DESIGN.md §13.8) |
|---|---|---|---|
| GitHub org `f-section` | github.com/f-section | Saran (`ssaravanan3`) | _TODO: name a trusted classmate_ |
| Cloudflare account | dash.cloudflare.com | Saran | _TODO_ |
| Domain `f-section.org` | _TODO: registrar_ | Saran | _TODO_ |
| Google Drive shared folders | _TODO: link_ | Saran | _TODO_ |
| NAS originals | `f-section/originals/` on the home NAS | Saran | n/a |

## Renewals
- [ ] Domain auto-renew is **on** (§13.9). Renewal date: _TODO_.
- [ ] The card on file at the registrar is current.

## Cloudflare resources (create only with Saran's go-ahead)

| Resource | Name | Status |
|---|---|---|
| Cloudflare account | Account ID `ba192ced071eda871cf3a8040e546047` | ✅ |
| DNS zone | `f-section.org`, zone ID `a02100991dd0671129fed18b193804f1`, nameservers `albert` and `kehlani.ns.cloudflare.com` | ✅ active |
| Worker (site) | `f-section-site`: Workers Builds from GitHub `f-section/f-section.org`, config in `wrangler.jsonc`, `NODE_VERSION=24` | ✅ created 2026-10-13 |
| Production branch | `main` → https://f-section.org (also https://f-section-site.asaravanan75.workers.dev) | ✅ live |
| Preview branch | `staging` → https://staging-f-section-site.asaravanan75.workers.dev | ✅ |
| Custom domain (site) | `f-section.org` and `www.f-section.org`, set in `wrangler.jsonc` `routes` | ✅ live 2026-10-13 |
| R2 objects | `public/site/og-default.jpg` (link-preview image) | ✅ uploaded 2026-10-13 |
| R2 bucket | `f-section-media`, location APAC, `r2.dev` URL **off** | ✅ created 2026-10-13 |
| R2 custom domain | `media.f-section.org`, minimum TLS 1.2 | ✅ connected 2026-10-13 |
| Access (members area) | Deferred to a much later version (D-14) | _later_ |

The site runs as a **Worker with static assets**, not a classic Pages project. It is what the Cloudflare dashboard creates by default now. Static file requests are free and unlimited. `_headers` works the same way. The 404 page and trailing slashes are set in `wrangler.jsonc`.

## First-time Cloudflare setup

Steps marked **Saran** need your login, or a grant of access that only you can give. Steps marked **Claude** can be run from Claude Code once the earlier steps are done.

### 1. Add f-section.org to Cloudflare (Saran)
1. Sign in at https://dash.cloudflare.com. Choose **Add a domain** (also called "Add site"), type `f-section.org`, and keep "Quick scan for DNS records" on.
2. Choose the **Free** plan.
3. Review the DNS records Cloudflare found. Keep any **MX** or **TXT** records for email on the domain. Delete old A or CNAME records for `f-section.org` and `www` that point at a parking page; Pages will add its own records.
4. Cloudflare shows **two nameservers**, like `xxx.ns.cloudflare.com` and `yyy.ns.cloudflare.com`. Copy both.
5. At your domain registrar (where you bought f-section.org):
   - If **DNSSEC** is on, turn it off first. You can turn it back on later, through Cloudflare.
   - Replace the domain's nameservers with the two Cloudflare ones, and save.
6. Back in Cloudflare, choose **Check nameservers**. The domain becomes **Active**, usually within an hour (at most 24 hours). Cloudflare sends an email when it does.
7. **SSL/TLS → Overview:** set the mode to **Full**. **SSL/TLS → Edge Certificates:** turn on **Always Use HTTPS**.

### 2. Turn on R2 (Saran)
1. In the dashboard, open **R2 Object Storage** and choose to enable or subscribe to R2. Cloudflare asks for a payment method, even for the free tier. Nothing is charged while storage stays under 10 GB. The ingest script warns at 8 GB.
2. Note your **Account ID**. It is shown on the R2 overview page, on the right. You need it for the rclone endpoint.

### 3. Connect the site to GitHub (Saran, done 2026-10-13)
The Git connection is made in the dashboard, because you grant the Cloudflare GitHub app access to the `f-section` organisation.
1. **Workers & Pages → Create → Import a repository** (Workers Builds). Authorise the **Cloudflare Workers and Pages** GitHub app on the **f-section** organisation, for the `f-section.org` repository only.
2. Settings used:
   - Worker name: `f-section-site`. It must match `name` in `wrangler.jsonc`.
   - Production branch: `main`
   - Build command: `npm run build`
   - Deploy command: `npx wrangler deploy` (the default)
   - Non-production branch deploy command: `npx wrangler preview` (the dashboard default). It needs the `previews` block in `wrangler.jsonc`; without it the staging build fails with "missing a previews block".
   - Build variable: `NODE_VERSION` = `24`
3. Every push to `main` builds and deploys. The site is at `https://f-section-site.asaravanan75.workers.dev`.
4. **Custom domain** (next step): **Workers & Pages → f-section-site → Settings → Domains & Routes → Add → Custom domain**. Add `f-section.org`, then `www.f-section.org`. Cloudflare creates the DNS records and certificates. To redirect `www` to the bare domain, add a **Redirect Rule** (Rules → Redirect Rules): `www.f-section.org/*` → `https://f-section.org/${1}`, status 301.

### 4. Create the R2 bucket and its domain (Claude, done 2026-10-13)
Run `wrangler login` once in a terminal (wrangler 4.x is installed globally) and approve in the browser. Then Claude runs:
```bash
wrangler r2 bucket create f-section-media --location apac
wrangler r2 bucket domain add f-section-media --domain media.f-section.org --zone-id a02100991dd0671129fed18b193804f1 --min-tls 1.2
```
(Or in the dashboard: **R2 → Create bucket** `f-section-media`, location hint **Asia-Pacific**. Then **Settings → Custom Domains → Add** `media.f-section.org`.)
Do **not** turn on the bucket's `r2.dev` public URL. The custom domain is the only public way in.

### 5. Create the R2 API token for rclone (Saran)
1. **R2 Object Storage → Manage R2 API Tokens → Create API token.** (Older dashboards call it "Manage API tokens", on the right of the R2 overview page.)
2. Fill in:
   - Token name: `rclone-f-section-ingest`
   - Permissions: **Object Read & Write**
   - Specify bucket(s): **Apply to specific buckets only** → `f-section-media`
   - TTL: **Forever**. Revoke it if the PC is ever lost.
3. **Create API Token.** The next page is shown **only once**. Keep it open for step 6. It shows:
   - **Access Key ID**
   - **Secret Access Key**
   - the S3 endpoint: `https://ba192ced071eda871cf3a8040e546047.r2.cloudflarestorage.com`
   Do not paste these into chat, email or any file in the repo.

### 6. Set up rclone on the Windows PC (Saran)
Run the interactive setup, so the secret never lands in your command history:
```bash
rclone config
```
Answer the questions:
1. `n` (new remote). Name: `r2`.
2. Storage: type `s3` (Amazon S3 compliant).
3. Provider: choose **Cloudflare**.
4. `env_auth`: `false`, or just press Enter.
5. `access_key_id`: paste the **Access Key ID**.
6. `secret_access_key`: paste the **Secret Access Key**.
7. `region`: press Enter (auto).
8. `endpoint`: `https://ba192ced071eda871cf3a8040e546047.r2.cloudflarestorage.com`
9. Edit the advanced config? `n`. Then `y` to keep the remote, and `q` to quit.

Because the token is limited to one bucket, add one advanced setting so rclone doesn't try to list or create buckets:
```bash
rclone config update r2 no_check_bucket=true
```

Test it. Each command should succeed and show 0 objects on a new bucket:
```bash
rclone lsf r2:f-section-media
```
```bash
rclone size r2:f-section-media
```
The config is saved in `%APPDATA%\rclone\rclone.conf`, outside the repo. Optionally, `rclone config` → `s` (set configuration password) encrypts it.

### 7. Upload the default link-preview image (Claude, done 2026-10-13)
`src/site.ts` points WhatsApp previews at `https://media.f-section.org/public/site/og-default.jpg` (1200 × 630). To change the image, edit and run `scripts/og/make_og_image.py`, **save it under a new name** (for example `og-default-v2.jpg`), upload it, then update `DEFAULT_OG_IMAGE`. The old object is never overwritten.
```bash
scripts\ingest\.venv\Scripts\python scripts\og\make_og_image.py
rclone copy --immutable --header-upload "Cache-Control: public, max-age=86400" scripts\ingest\out\public\site r2:f-section-media/public/site
```

## Local tools (Windows PC)
- Node 22.12 or later, Git, the GitHub CLI (`gh`), and Python 3.12 or later with `scripts/ingest/.venv`.
- `rclone` (installed 2026-10-12 with `winget install Rclone.Rclone`), with a remote named `r2` set up as in step 6 above. The rclone config stays on the PC and never goes into git.
- `ffmpeg`, for video and audio: `winget install Gyan.FFmpeg` (installed 2026-10-12)
- `exiftool`, for inspecting photo metadata: `winget install OliverBetz.ExifTool` (installed 2026-10-12)
- NAS mapped as a drive letter (for example `Z:`).

## Branches
- `main` is production and protected. Changes reach it only by pull request from `staging`.
  - GitHub branch protection (free, because the repo is public) requires a pull request and passing `site` and `ingest` checks. It applies to admins too. 0 approvals are needed, so Saran can merge his own pull requests.
  - A local pre-push hook also blocks `git push` to `main`. Enable it once per clone with `git config core.hooksPath .githooks`.
- `staging` is where all work happens. Cloudflare builds a preview for every push.

## Rolling back
1. **Site:** open the Cloudflare Pages dashboard, go to Deployments, choose the last good one and select "Rollback". Then `git revert` the bad commit on `staging`, open a pull request and merge it, so the code matches what is live.
2. **Media:** objects in R2 are never overwritten, because new versions get new names. Point `media.json` back to the old id.
3. **Removing a photo (takedown):** remove its entry from `media.json` and deploy. Deleting the object from R2 is a separate, manual step. List the exact keys first and get Saran's "yes". There is no automated delete command yet.

## Storage budget
The R2 free tier is 10 GB. The ingest script prints the bucket size after every upload and warns at 8 GB.

## Backups (3-2-1)
1. Originals on the NAS: `f-section/originals/<album-slug>/`
2. External drive, kept offline: _TODO: schedule_
3. Google Drive: _TODO: folder_

R2 is where the site's media lives. It is **not** a backup.

## Montage title cards (scripts/video)
The title cards in the 30-year reunion montage were redone to match the site (2026-10-14). The original iMovie export stays unchanged in `E:\F Section\Finalized Articles\`; the new master is `E:\F Section\Claude outputs\30_Year_Video_montage_v3.mp4` (4 new cards, song completed under the end card).
1. Edit the cards in `scripts/video/cards/*.html` (shared style in `card.css`).
2. Render them at 4K: `node scripts/video/render-cards.mjs --scale 2 --cover "<final front cover>" --back "<final back cover>"` (both in `E:\F Section\Claude outputs\Montage cards (draft)\`)
3. Lay them over the montage: `scripts\ingest\.venv\Scripts\python scripts\video\replace_cards.py --src "<iMovie export>" --song "<song .mp3>" --out "<new master>.mp4"`. Card timings are in `scripts/video/montage-2026-30th.json`. The montage audio up to 4:14.67 is kept as it is, so the music sync never changes. With `--song`, the end card (`04-ending`) is added and the same song (the montage uses it from 0 s) continues under it, fading out on a pause at 4:28. The song file stays in `E:\F Section\Claude outputs\`, never in git.
4. Make the web copies (1080p at 5 Mbps, 720p at 2.5 Mbps, poster) under a **new name**, and upload them with `rclone copy --immutable` to `public/video/`.
