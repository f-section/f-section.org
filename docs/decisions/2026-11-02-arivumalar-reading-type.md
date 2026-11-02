# Arivu Malar: the reading page set as a book

**Date:** 2026-11-02
**Decided by:** Saran, after reading the live edition.
**Changes** the "Look" row of [2026-10-31-arivumalar-ebook-shape.md](2026-10-31-arivumalar-ebook-shape.md),
which said "no new fonts": the reading column now has a serif of its own.
**Affects:** DESIGN.md §10.4; `src/styles/global.css`; `src/pages/[...lang]/arivumalar/[issue]/[section].astro`;
`scripts/arivumalar/extract.py`; `scripts/arivumalar/media.py`; R2 `public/arivumalar/2026/then/`

## What Saran asked for

Five things, after reading the book on the site: the three 1996 portraits he had cropped out of the
printed book put in; the pictures inside articles made smaller, because they were breaking the
reading; the text itself made smaller and set in a face that reads like a Tamil book, with
[tamilsurangam.in](https://www.tamilsurangam.in/literatures/kambar/index.html) as the size he reads
comfortably; the headings set the way the printed book sets them; and `கவிதை` over every poem, the
way the stories say `கதை`.

## Decided

**The face.** Noto Serif Tamil, self-hosted from @fontsource like the other two, 400 and 600, latin
and tamil subsets. The same family as the body face, so the two sit together, and a serif is what a
Tamil book is set in. The four subset files are 12–16 KB each and are fetched only on a page that
draws them, so the album pages carry nothing new.

**The size.** 17px over a 36em measure — about 35 Tamil characters a line — with the leading Tamil
script needs. The reference page sets its Tamil at 12px in whatever face the reader's system has;
that is too small for readers who are mostly past fifty, and rule 7 puts the site's base at 18px.
17px in a serif reads smaller than 18px in the sans and keeps the rule's intent. This column is the
only exception on the site: everything outside it stays at 18px in Noto Sans Tamil. It is one number
in `global.css` if Saran wants it a step smaller or larger.

**Pictures in an article** are capped at about two-thirds of the column and centred — 23em wide,
21em tall, 16em tall on a phone — in either orientation, and the viewer still opens one full size. A
picture in the middle of an article is a glance, not a stop.

**The heading** follows the print: the kind of piece above in small letterspaced capitals, the title
in `ink-red` with the half after a colon pushed out to the right margin, the author's name under a
short red rule, letterspaced and quieter. Tamil has no italic face, so the rule, the colour and the
letterspacing do the work the print's italic did — a slanted Tamil face would be a synthetic oblique
and read badly. On the In Memoriam page, which prints on ink, the title takes the paper colour and
the rest `rule`: red on dark would not carry. The heading also stands over its own column now
instead of the whole screen.

**The kind of piece.** `கவிதை` for the poems, `கதை` for the stories, `கட்டுரை` for the articles and
the memoirs, then the issue's name. Where the print used a word that is not a kind, it is kept after
it: `கவிதை · நினைவஞ்சலி`, `கவிதை · தொகுப்பு`. The puzzles and the picture spreads keep the line the
book gave them. `kicker_for()` in `extract.py` does it, so a re-run of the extractor keeps it.

**The three crops.** `வைரமுத்து` and `ஸ்ரீதர்` had no 1996 portrait at all; `மோகன் சுகுமார்`'s crop
replaces the export's own scan of him, under a key of its own, so nothing in R2 was overwritten.
They are 105–158px wide, so `media.py` stops the frame at twice the crop instead of pulling it to
320 and inventing detail, softens nothing and sharpens less, and reads them as grey, since a
photograph of a printed page carries a colour cast the printed page never had.

## Notes

- `rclone copy --immutable` now reports a timestamp mismatch on the sixteen thumbnails already in
  R2, because a re-run of `media.py` rewrites every file. That is the guard refusing to touch them,
  not a failure: their bytes are unchanged, and only the three new keys were uploaded.
- The printed bylines of two articles carry a surname as well as a first name, because they are the
  book's own words on the page. Rule 14 is about how the site names people; left as printed.
