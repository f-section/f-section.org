# People are named by first name only

**Date:** 2026-10-26
**Approved by:** Saran
**Affects:** DESIGN.md §4.4, §10.5; CLAUDE.md; every title, caption and file name

## What changed
Everywhere a person is named on the site, use the **first name only**: `Kumaravel`, not
`Kumaravel Saravanan`. This covers video and album titles, captions, media file names, slugs and
the `people/` collection, in both languages.

## Why
That is how this batch of friends knows one another, and has for thirty years. The site is a
reunion album, not an official register, and full names would read as stiff and slightly formal
to the people it is for. The media naming rule already used the contributor's first name
(`..._saravanan_...`), so this makes the rest of the site agree with it.

## What prompted it
The first draft of the kavithai video title read "a kavithai by Kumaravel Saravanan". That name
does not exist: it ran together Kumaravel, who wrote and recited the poem, and Saravanan, which is
Saran. Claude had transliterated it from the English credit line on the poem image without
checking. A friend's name, misspelt on his own poem, on a public page.

## Notes
- `src/content/people/` has no entries yet, so there is nothing to migrate. §10.5 now shows
  `slug: firstname`.
- Where two people share a first name, add the least that tells them apart, and ask Saran which
  form he wants rather than choosing one.
- **Tamil spellings of names are Saran's to give.** Claude does not transliterate a person's name
  into Tamil; it asks. The same draft had `குமரவேல்` where Saran writes `குமாரவேல்`, and
  `உச்சி பிள்ளையார்` where the correct form is `உச்சிப் பிள்ளையார்`.
