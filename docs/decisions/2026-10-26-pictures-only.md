# The gallery shows pictures only

**Date:** 2026-10-26
**Approved by:** Saran
**Affects:** CLAUDE.md rule 6; DESIGN.md §6.3, §8.1; `src/pages/[...lang]/gallery/[era]/[album].astro`

## What changed
Under each photo the album page used to print `Photo: <contributor>` and a 📍 **Show on map** link.
Both are gone. A photo now shows nothing beneath it unless it carries a caption, and the only
captions in the gallery are the five department groups.

## Why
Saran saw the first two real albums and said the lines under the pictures looked wrong. He is
right: the gallery is for looking at, the credit repeats on nearly every frame in an album (20 of
the 31 campus photos are Mohanraj's), and a map link invites a click that leads away from the page
to somewhere nobody wanted to go.

## What this does *not* change
- **GPS is still kept**, both in the display copy's EXIF and as coordinates in `media.json`. It is
  simply not shown. Nothing is stripped, so a map or a Places page can use it later without
  re-ingesting anything.
- **`credit` is still recorded** in `media.json`, so who took which photo is never lost.
- `mapUrl()` stays in `src/lib/media.ts`, unused for now.

## Worth revisiting
With nothing displaying them, the coordinates in `media.json` sit in a public repo for no
user-facing reason. They are also in `originals/<album>/manifest.csv`, which is outside git. If
that bothers Saran later, they can be dropped from `media.json` without losing anything.
