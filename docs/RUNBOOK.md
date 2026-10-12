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
| Pages project | `f-section-org`, from GitHub `f-section/f-section.org` | _not created_ |
| Pages build | Command `npm run build`, output `dist`, Node 22 or later | _not created_ |
| Production branch | `main` → f-section.org | _not created_ |
| Preview branch | `staging` → preview URL, protected by Access (one seat) | _not created_ |
| R2 bucket | `f-section-media`, custom domain `media.f-section.org` | _not created_ |
| Access (Phase 2a) | `/members/*` on f-section.org and media.f-section.org | _later_ |

## Local tools (Windows PC)
- Node 22.12 or later, Git, the GitHub CLI (`gh`), and Python 3.12 or later with `scripts/ingest/.venv`.
- `rclone` with a remote named `r2` pointing at the Cloudflare R2 account. Use an R2 API token scoped to `f-section-media` with **Object Read & Write** only. The rclone config stays on the PC and never goes into git.
  ```bash
  winget install Rclone.Rclone
  rclone config
  ```
  Choose: new remote `r2`, type `s3`, provider `Cloudflare`, then the access key, secret and endpoint from the R2 dashboard.
- `ffmpeg`, for video and audio: `winget install Gyan.FFmpeg`
- NAS mapped as a drive letter (for example `Z:`).

## Branches
- `main` is production and protected. Changes reach it only by pull request from `staging`.
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
