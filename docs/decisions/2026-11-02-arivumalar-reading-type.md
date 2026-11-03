# Arivu Malar: the reading page set as a book

**Date:** 2026-11-02
**Decided by:** Saran, after reading the live edition.
**Changes** the "Look" row of [2026-10-31-arivumalar-ebook-shape.md](2026-10-31-arivumalar-ebook-shape.md),
which said "no new fonts": the reading column now has a serif of its own.
**Changed in turn by** [2026-11-03-arivumalar-reading-page.md](2026-11-03-arivumalar-reading-page.md):
the size, how a picture sits, the captions and a poem's kicker were all settled a day later.
**Affects:** DESIGN.md §10.4; `src/styles/global.css`; `src/pages/[...lang]/arivumalar/[issue]/[section].astro`;
`scripts/arivumalar/extract.py`; `scripts/arivumalar/media.py`; R2 `public/arivumalar/2026/then/`

## What Saran asked for

Five things, after reading the book on the site: the three 1996 portraits he had cropped out of the
printed book put in; the pictures inside articles made smaller, because they were breaking the
reading; the text itself made smaller and set in a face that reads like a Tamil book, with
[tamilsurangam.in](https://www.tamilsurangam.in/literatures/kambar/index.html) as the size he reads
comfortably; the headings set the way the printed book sets them; and `கவிதை` over every poem, the
way the stories say `கதை`. Then, on the first pass: the type smaller still, and the pictures set
inline with the text rather than stacked above and below it.

## Decided

**The face.** Noto Serif Tamil, self-hosted from @fontsource like the other two, 400 and 600, latin
and tamil subsets. The same family as the body face, so the two sit together, and a serif is what a
Tamil book is set in. The four subset files are 12–16 KB each and are fetched only on a page that
draws them, so the album pages carry nothing new.

**The size.** 15.75px over a 38em measure, with the leading Tamil script needs. The first pass set
it at 17px, reasoning from rule 7 that readers past fifty need the larger type; Saran's answer was
that age should not decide it — the book is not read only by the class of '96, and they read smaller
type everywhere else all day. So it is set at the size a book is set at, which is also close to what
his reference page does. This column is the only exception on the site: everything outside it stays
at 18px in Noto Sans Tamil, and rule 7 is unchanged for the rest. It is one number in `global.css`.

**Pictures sit in the text, as a magazine sets them** (Saran, 2026-11-02). The picture's own
paragraph floats, so it takes about a third of the column and the article runs on beside it, and
they alternate sides down the page. A standing portrait is held by its height rather than its width,
so it comes out as the narrow strip a printed page would give it. A heading or a break starts clear
of the picture. Below 40rem there is no room beside one, so it keeps its own line, centred, 15em
tall. The viewer still opens one full size.

**Captions.** The book sets a caption as a bold line under the picture, and the export keeps it as a
paragraph of nothing but bold text. Such a paragraph, when it follows a picture, is read as that
picture's caption and set like one — small, sepia, unbolded, floated under the picture on a wide
screen and centred under it on a phone. Seven of them in this issue; nothing else in the book
matches that shape, so no body text is caught by it.

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
