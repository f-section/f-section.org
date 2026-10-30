# Moving between photos, and starting a video again

**Date:** 2026-10-30
**Asked for by:** Saran, after looking at the first two 30th-reunion albums on the live site.
**Affects:** DESIGN.md §6.3; `src/components/Lightbox.astro`, `src/components/VideoPlayer.astro`,
`src/pages/[...lang]/gallery/[era]/[album].astro`, `src/i18n/*.json`

## What was wrong
Tapping a photo opened its large copy as a bare image on `media.f-section.org`. To see the next
one you had to press Back and find it in the grid. With 37 photos in an album that is 36 trips
back and forth.

On the videos page, the browser's own controls give play, mute, full screen and a slider —
but no way back to the start except dragging the slider, which is fiddly on a phone.

## What we do now
**Photos.** The album page still links every photo to its large copy. A small script turns those
links into a full-screen viewer: **first · back · forward**, a `3 / 37` counter, and a close
button. A sideways swipe moves between photos; the arrow keys, `Home` and `Escape` do the same on
a computer. The controls sit at the bottom, within thumb reach, and are drawn in paper at 75%
over the dark backdrop so they stay out of the way of the picture.

**Videos.** Each video gets a **Start from the beginning** button under it, next to the running
time, with a ⏮ mark. It rewinds that video and plays it.

## Why it is built this way
- **The link comes first.** The viewer is layered on top of plain `<a href>` links, so an old
  phone, a locked-down browser or a failed script leaves the album exactly as it was before.
  The script checks for `<dialog>` support and simply does nothing if it is missing.
- **No new dependency.** About 90 lines of plain JavaScript, no Alpine, no gallery library.
- **One list, not two.** The viewer reads the photos out of the page it is on
  (`a[data-lb-item]`), so there is no second copy of the album to keep in step with `media.json`.
- **Focus goes to the viewer itself,** not to a button, so no control is left wearing a focus
  ring on top of the photo. Arrow keys and `Escape` still work.

## Tamil
Six new interface strings (`lightbox.*`, `videos.restart`) were drafted by Claude under rule 5
and need Saran's eye: படக் காட்சி, முதல் படம், முந்தைய படம், அடுத்த படம், மூடு,
தொடக்கத்திலிருந்து பார்க்க.
