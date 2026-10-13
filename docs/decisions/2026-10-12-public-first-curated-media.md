# Public-first site; curated media keeps its location

**Date:** 2026-10-12
**Approved by:** Saran
**Affects:** DESIGN.md D-12, D-14 (new), §8.1, §13.1–13.3; CLAUDE.md rule 6

## What changed
1. **Public-first.** Build a simple public website now. Email logins and the members area for friends and family (Phase 2, O-1) come much later, in version 3 or 4.
2. **Media is vetted before ingest.** Saran and friends check every photo by hand. Anything given to the ingest script is cleared to publish as is. The site runs no consent checks of its own.
3. **GPS is kept, not stripped.** Location is useful: photos are taken in different places, and the site shows a "Show on map" link for any photo or video that has coordinates. The ingest script:
   - keeps the EXIF (date, GPS, camera) in the 2048 px display copy
   - writes `gps: { lat, lon }` into `media.json`
   - leaves the 480 px thumbnails without metadata, to keep them small

## Unchanged
- In Memoriam still needs `family_consent: true` and stays members-only.
- Public videos still need `music_cleared: true`.
- No phone numbers or addresses anywhere.
- `noindex` stays on (O-2).
