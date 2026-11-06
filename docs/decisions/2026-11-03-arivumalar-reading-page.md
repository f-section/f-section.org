# Arivu Malar: the reading page after the third read

**Date:** 2026-11-03
**Decided by:** Saran, after reading the staging preview of [2026-11-02](2026-11-02-arivumalar-reading-type.md).
**Changes** that note: the type is smaller again, the printed captions are off the page, and a
poem's kicker no longer keeps a second word.
**Changed in turn by** [2026-11-05-arivumalar-fourth-read.md](2026-11-05-arivumalar-fourth-read.md):
the tribute keeps `நினைவஞ்சலி`, and the nav at the top of a page names the pages it leads to.
**Affects:** DESIGN.md §10.4; `src/styles/global.css`; `astro.config.mjs`;
`src/components/ebook/Reader.astro`; `src/i18n/*.json`; `scripts/arivumalar/extract.py`

## What Saran asked for

Five things: the type a step smaller still; the floated pictures fixed, because in some pieces they
came out small and pinned to the right with nothing beside them, and bigger, with Constan's last two
set side by side rather than one above the other, the caption off if it is in the way; `கவிதை` over
every poem and nothing else; one author's name over a piece, not two; and `முன்` / `பின்` at the
top of a reading page as well as at the foot.

## Decided

**The size.** 14.6px (0.8125rem), a step below the 15.75px he read. Same face, same 38em measure.

**A picture sits according to what follows it.** The first pass floated every picture, which only
works where a paragraph comes after it to run alongside. Where the book put a picture just before a
heading, a pull-quote or the end of a piece — more than half of them in this issue — the float left
a small picture against the right margin with an empty line beside it. So:

* `eb-flow` — a paragraph follows: the picture floats to 15em (up from 13em) and the text runs on
  beside it, the pictures alternating sides down the page. A standing portrait is held by its
  height, 20em, and comes out as a narrow strip.
* `eb-pair` — the next block is another picture: the two stand side by side, each half the column.
* `eb-wide` — anything else follows: the picture stands on its own, centred, as wide as the column
  and up to 24em tall.

CSS cannot ask what follows an element, because `:has()` may not be nested inside `:has()`, so the
hast plugin in `astro.config.mjs` works it out in its `after` hook and writes the class on the
picture's paragraph. A Chrome detail: a picture whose height is what holds it keeps its full width
when the auto margins are resolved, so `margin-inline: auto` leaves it against the left edge — the
paragraph is a centring flex container instead.

**The printed captions are off the page.** The book sets a caption as a bold line under the
picture, and it stood between the picture and the text it belonged to. `extract.py` now folds the
caption into the picture's `alt` — which is what the photo viewer and a screen reader read — and
drops the line, so the words the book printed are still in the file and nothing is invented.

**One name over a piece.** The book repeated the author's name at the top of three pieces, under a
heading that already carries it. `extract.py` drops a short line among the first blocks of a piece
that is only the author's name: `பாஞ்சாலை நடராஜன்`, `முகமது இஸ்மாயில்`,
`லெப்டினன்ட் கமாண்டர் (ஓய்வு) கான்ஸ்டன்`. The sign-off at the *end* of
`இந்தியாவின் எஃகு தொழில்` is the book's own and stays.

**The kicker is one word.** `கவிதை · அறிவு மலர் 2026` over every poem. The first pass kept a second
word where the print had one — `கவிதை · நினைவஞ்சலி`, `கவிதை · தொகுப்பு` — and page after page
those read as different kinds of piece. The tribute still says who it is for, in the dedication
line under its title.

**Turning the page from the top.** `முன்` / `பின்` (shorter than the first pass's `முந்தையது` /
`அடுத்தது`) sit above the heading as two labels, and the foot keeps the same pair with the titles
they lead to. A piece of six thousand words otherwise meant scrolling all the way down to turn the
page.

## Notes

- Editing `astro.config.mjs` alone does not invalidate Astro's content cache: the pictures came out
  unclassified until `.astro` and `node_modules/.astro` were removed. Workers Builds starts from a
  fresh clone, so this is a local trap only.
- The pair rule places two pictures in a row. A run of three would put the first two side by side
  and leave the third standing alone; no piece in this issue has one.
