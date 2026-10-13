# Site hosted as a Cloudflare Worker, not a Pages project

**Date:** 2026-10-13
**Approved by:** Saran (created the project in the dashboard)
**Affects:** DESIGN.md D-03, §7, §12; RUNBOOK

## What changed
The Cloudflare dashboard's "Connect to Git" flow now creates a **Worker with static assets** (Workers Builds) by default, and Saran created `f-section-site` that way. We keep it, because:
- Static file requests are free and unlimited, as on Pages.
- `_headers` works the same way.
- Builds run on every push. `main` deploys to production, and other branches get preview URLs.
- It is the product Cloudflare is moving Pages users towards.

## Repo changes
`wrangler.jsonc` sets:
- `assets.directory = ./dist`
- `not_found_handling = 404-page`, so unknown URLs show our 404 page. Without it, the response is an empty 404.
- `html_handling = auto-trailing-slash`
- `preview_urls = true`, so `staging` gets a preview URL.

The Worker name, `f-section-site`, must match the name in the dashboard.

## Names and IDs (not secrets)
- Account `ba192ced071eda871cf3a8040e546047`
- Zone `f-section.org`, ID `a02100991dd0671129fed18b193804f1`
- R2 bucket `f-section-media` (APAC), served at `media.f-section.org`
