# Media ids stay short; place is optional metadata

**Date:** 2026-10-26
**Approved by:** Saran
**Affects:** DESIGN.md §4.4; `docs/decisions/2026-10-25-gallery-import-and-curation.md`

## What changed
A published media id is

```
<YYYYMMDD>-<HHMMSS>_<contributor>_<NNN>
20261003-184212_saravanan_001
```

with **no place-or-event segment**. The same name is used in the work area and in the manifest's
`new_name`, so a file keeps one name from download to R2 and nothing has to be translated between
stages.

Where a photo's place is already known, it goes in `media.json` as `place`, pointing at an id in
`places.yaml`, and the album lists the places it covers. Where it is not known, the field is left
out. **Nobody goes looking.**

## Why
The 2026-10-25 curation note specified `..._place-or-event_NNN`, and DESIGN.md §4.4 repeated it,
but the code never did: `scripts/ingest/ingest.py` builds ids as
`f"{taken:%Y%m%d-%H%M%S}_{contributor}_{n:03d}"`, and `src/lib/media.ts` validates them against
`/^(\d{8}-\d{6}|\d{4}-00-00)_[a-z0-9]+_\d{3}$/`. A place-bearing id would have failed the build.

Asked to choose, Saran picked what suits the build: the place was only ever there for clarity, and
it is not worth spending time deriving one for each of hundreds of files. Only 92 of the 563
photos carry GPS, and all of them come from two contributors, so a place segment would have been
guesswork on most files anyway.

It is also the better shape. A place in a key is a place that cannot change; a place in
`media.json` can be corrected later without touching R2, where objects are never overwritten.

## Notes
- `places.yaml` was filled out at the same time with the campus and Trichy spots the reunion
  albums need. Tamil names are left empty and fall back to English until Saran writes them.
- Photos that do carry GPS keep it: the site shows a map link per photo (CLAUDE.md rule 6), and
  that is independent of `place`.
