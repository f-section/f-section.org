# No consent or music gates; site open to search engines

**Date:** 2026-10-12
**Approved by:** Saran
**Affects:** DESIGN.md D-10, D-13, §8.2, §10.3, §10.5, §10.6, §13.5, §13.7, O-2, O-5; CLAUDE.md rule 6

## What changed
1. **In Memoriam has no `family_consent` gate and is public.** Friends and families have agreed in advance, and Saran curates every entry. If anyone raises a concern, the entry is taken down by hand.
2. **Videos have no `music_cleared` gate.** Montages use film songs from our college years as background music, because they are what makes the memories land. If a rights holder objects, take the video down or change the soundtrack.
3. **People entries** no longer need a `consent` block and are no longer limited to members.
4. **Every collection defaults to `visibility: public`.**
5. **The site is open to search engines** (closes O-2). `noindex` was removed, and `robots.txt` and `sitemap-index.xml` were added. Only `/styleguide/` and the 404 page stay `noindex`. Cloudflare marks staging previews `noindex` automatically.

## Why
These gates blocked the group from moving forward. The real safeguard is hand curation by a small, trusted group, with takedown on request.

## Still checked by the build
- Schemas: field types, slugs and dates.
- R2 keys must start with the item's visibility prefix, so links don't break.
- No phone numbers.
- WCAG AA contrast.
