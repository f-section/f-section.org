# Arivu Malar: the reading pages after the fourth read

**Date:** 2026-11-05
**Decided by:** Saran, reading the staging preview of [2026-11-03](2026-11-03-arivumalar-reading-page.md).
**Changes** that note on two points: the tribute's kicker keeps a second word after all, and the
nav at the top of a page names the pages it leads to.
**Affects:** DESIGN.md §10.4; `scripts/arivumalar/extract.py`; `scripts/arivumalar/media.py`;
`scripts/arivumalar/proof.py`; `src/components/ebook/Reader.astro`;
`src/components/ebook/SpotSix.astro`; `src/content.config.ts`;
`src/pages/[...lang]/arivumalar/[issue]/[section].astro`; R2
`public/arivumalar/2026/img/unnal-mudiyum-thambi-picture.webp`

## What Saran asked for

Eight things, reading the issue through on staging: `நினைவஞ்சலி` back over the tribute; the titles
of the pages before and after under `முன்` / `பின்` at the top of a page, as they already are at the
foot; குமாரவேல்'s `மாறாத மனிதர்கள்` and `என் கவிதைக்கு வயதாகவில்லை` to change places; the page of
his two short poems named `நிழல்கள்` and each poem given its own title; `ஒலித்து கொல்` to open with
its words rather than its picture, the picture smaller and further down; the answers to
`ஆறு வித்தியாசங்கள்` in words alone, without the marked-up third picture; the colour original of the
award picture in `உன்னால் முடியும் தம்பி` in place of the printed black and white one; and the
closing notes of `வரிசையில் என்ன உள்ளது` turned into links, to three addresses he gave.

## Decided

**The tribute says what it is.** `கவிதை · நினைவஞ்சலி · அறிவு மலர் 2026` over `முகவரியற்றவர்கள்`,
and that page alone (`KEEP_PRINTED` in `extract.py`). Two days ago every second word came off the
kickers, so that page after page would not read as a different kind of piece; this one is worth the
exception, because the poem is a tribute before it is a poem. `தொகுப்பு` over the collected poems
stays gone.

**Turning the page names the page.** The nav above the heading now carries the title it leads to,
the same markup as the foot. A label on its own said which way to go but not where to. On a phone
the two titles take two or three lines before the heading; the bottom nav already does the same, and
knowing what is next is worth the lines.

**The two poems have two titles.** The page is `நிழல்கள்`, after the first poem, and inside it
`## நிழல்கள்` and `## நீயிருக்கும் வகுப்பறை` stand over their own verses. The thematic break between
them is gone. The 2026-10-31 reading — that the second poem's first line was its title — was wrong:
Saran knows what they are called.

**A piece opens with its words.** Where the book put a picture at the head of a piece, it drops
below the first paragraph of prose. In `ஒலித்து கொல்` that also makes it smaller, because a picture
with a paragraph after it floats into the text at 15em instead of standing the width of the column.
`lead_text` on the section says so; `என்றென்றும் அழியாத நினைவுகள்` opens with a picture in the same
way and is left as it is, not having been asked about.

**The six differences are read, not spotted.** The two pictures of the puzzle, and the six answers
in words behind the விடைகள் button. The book marks them on a third copy of the picture, which told
the answer before the words could. `answer_photo` is gone from the schema, the component and the
extractor; the marked picture stays in R2, unreferenced — nothing in the bucket is ever deleted.

**The award picture in colour.** The printed book carried it in black and white, which is what the
design export scanned; Saran has the colour original. It sits in `incoming/crops/` beside the
export, like the three 1996 portraits, and `SWAPS` in `extract.py` puts it in place of the export's
scan under a key of its own, so the export is untouched and nothing in R2 is overwritten. It is an
ordinary photograph, not a 1996 portrait, so `media.py` now decides the pass from the picture's key
— only `then/` goes through the portrait one — rather than from where its file sits.

**The closing notes are links.** `NOTE_LINKS` in `extract.py` holds Saran's three addresses, in the
order the notes stand, and the line is shortened to its description, because the link carries the
address. Two of the three now lead to tamilvu.org where the printed line named Project Madurai;
they are his addresses for the same commentary, and the page no longer shows an address it does not
go to.

**The reading order.** `மாறாத மனிதர்கள்` and `என் கவிதைக்கு வயதாகவில்லை` changed places — 6 and 19.
The order is the order of `SECTIONS` in `extract.py`, written out to `order:` in `2026.yaml`.

## Notes

- `--verify` accounts for every run of text in the export again: the three shortened note lines and
  the two repeated bylines dropped on 2026-11-03 are now listed in `DROPPED` with their reasons.
- Only the one new key was uploaded to R2, with `rclone copyto --immutable`, so no existing
  object's bytes or timestamps were touched.
