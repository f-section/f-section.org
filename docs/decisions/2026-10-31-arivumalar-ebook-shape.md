# The Arivu Malar 2026 e-book: two modes, reflowed text, and where the text comes from

**Date:** 2026-10-31
**Decided by:** Saran, answering seven questions on 2026-10-30 and 2026-10-31.
**Replaces** the proposal in [2026-10-30-arivumalar-2026-ebook.md](2026-10-30-arivumalar-2026-ebook.md)
wherever the two disagree.
**Affects:** DESIGN.md §3, §6.3, §10.4; `src/content.config.ts`;
`src/content/arivumalar/2026/`; `scripts/arivumalar/extract.py`; R2 `public/arivumalar/2026/`

## What changed from the 2026-10-30 proposal

| | 10-30 proposal | Decided |
|---|---|---|
| Modes | three: read online, book view, PDF | **two**: read online and the PDF. No page-image book view. |
| Text source | Claude Design HTML, falling back to `.docx`, then OCR | **the Claude Design HTML only.** It holds the Tamil live in the markup, so no OCR and no `.docx` pass. |
| Look | the book's own cream, terracotta and Noto Serif Tamil | **the site's existing look**: paper, ink, ink-red, Noto Sans Tamil. No new fonts. |
| Page images | 71 pages × 3 sizes rendered with `pdftoppm` | **none.** Nothing to render, no poppler, no Ghostscript. |
| Profiles | one collection, layout unstated | **an index plus one page per person**, each `noindex`. |
| Reading order | a new web order worked out up front | **the printed order first.** Saran reorders after reading it on the web. |
| Names | the book's full names | **first names only** (rule 14), with `printed_name` keeping what the book printed. Some Tamil first names run to two words with the surname separate, so மோகன் சுகுமார் and இரமேஷ் கண்ணன் are first names, not name plus surname (Saran, 2026-10-31). |

## The shape

| URL | What it is |
|---|---|
| `/arivumalar/` | What Arivu Malar is, a card for the 2026 issue, a note that the 1992–96 archive comes later |
| `/arivumalar/2026/` | The issue page: front cover, **பொருளடக்கம்**, **முகப்பு** into the book, **தரவிறக்கம் · 39.5 MB** |
| `/arivumalar/2026/<slug>/` | One reading page per section, 27 of them |
| `/arivumalar/2026/then-and-now/` | The `அன்றும் இன்றும்` index: 19 names with their `இன்று` photo. It is a reading page like any other, so it keeps its place in the order — there is no second index at `/people/` |
| `/arivumalar/2026/people/<name>/` | One page per person — **`noindex`** |

The `/ta/` mirror carries the same pages; the chrome follows the language toggle and the magazine
text is Tamil on both, since there are no English titles for now.

**Reading UI.** A **பொருளடக்கம்** button in the page header opens the contents over the page — the
same native `<dialog>` as the Lightbox, so no new dependency — and the reading column has the
screen to itself at every width. A sticky sidebar of the 27 titles from 1024px up was built first
and dropped on 2026-10-31 (see below). Each section ends with prev · next in the configured order
and a link back to the issue page.

**Typography.** 18px Noto Sans Tamil, 1.8 line height, a ~34em measure, paper/ink/ink-red. The A5
design is not reproduced: at 8.2pt a scaled A5 page lands near 6px on a phone, which rule 7 rules
out. The printed look lives in the PDF.

**Photos** run inline where the design placed them — floated beside the text on a computer, full
width above it on a phone — and tap into the existing Lightbox. The design's floats are in mm and
are not carried over.

**The poems are scattered, not collected.** In print, `கவிதைகள்` was a nine-page set and two more
of குமாரவேல்'s short poems sat on the leftover half of his own profile page, filling space the A5
sheet could not use. The web has no such constraint, so the poems are spread between the essays and
the stories: nine reading pages, six of them குமாரவேல்'s. `மூச்சுவிடும் தூரம்` was likewise filler
on the puzzle answers page and now stands alone. The two off the profile page are short, so they
share one page — `நிழல்கள் · நீயிருக்கும் வகுப்பறை`, with a `***` break between them (Saran,
2026-10-31). `நிழல்கள்` is the title Saran gave the first; the second had none in print, so its own
first line stands as its title.

**The third photograph.** Each profile can also show them speaking on the night the book was
released (Saran, 2026-10-31): `அன்று`, then release night, then the family picture as `இன்று`. It
is a tag pointing into the `2026-reunion-arivu-malar` album, not a new upload, so the picture is
the one already on the site and the profile links back to the album. Only `அன்று` and `இன்று` are
captioned — two labels for three pictures (Saran, 2026-10-31) — because the release-night picture
belongs to today as much as the family one does.

**Alt text stays empty** where the print design had none (Saran, 2026-10-31): a photo described
for the sake of it reads awkwardly, and the text beside it already carries the meaning. The pages
therefore emit `alt=""`, which is the correct way to mark a picture as decorative — not a missing
attribute. **No exceptions** (Saran, 2026-10-31): கான்ஸ்டன்'s four essay photographs were held
open for captions through the design hand-over, and Saran has now closed it — the magazine is in
Tamil, and an English caption under a Tamil page's photograph would be the one piece of the book
written for the website rather than taken from it. They stay as the design had them, uncaptioned.
This is the e-book only: DESIGN.md §6.4 still holds for the gallery.

**Puzzles** stay HTML, not page images: the crossword is a real CSS grid with its clues, and the six
differences are two pictures. Both keep their answers behind a **விடைகள்** button, which also
leaves the door open to making them interactive later.

## Where the text comes from

`design/*.dc.html` in the Claude Design export. Each file is a finished print page with the Tamil
live in the markup, so `scripts/arivumalar/extract.py` reads the DOM, decides which run of text is
a heading, a paragraph, a poem line, a pull-quote, a byline or a photo, and writes the content
files. Every string is copied byte for byte; nothing is OCR'd, retyped, reflowed or translated.
`--verify` re-reads the export and reports any run of text that did not reach a content file.

**`uploads/அறிவுமலர் - நினைவுகள்.json` is deliberately not read.** It carries email addresses and
Google Drive links (rule 10), it covers only the first 14 of the 19 people, and its answers predate
the edits made during design. The printed HTML is the authority.

## The content model

- **`src/content/arivumalar/2026.yaml`** — the issue. New fields: `cover`, `cover_back`,
  `pdf_bytes`, and **`order`**, the list of section slugs that sets the web reading order. That one
  list is the only place to change it, which is why the order is not in the filenames.
- **`src/content/arivumalar/2026/sections/<slug>.md`** — one reading page. The Tamil body is
  Markdown, verbatim; a trailing `\` keeps a printed line break. `![alt](r2:public/…)` marks a
  photo that lives in R2, and the `r2:` scheme keeps Astro's image pipeline out of it.
  `type` picks the layout: `article · memoir · story · poem · humour · photos · scans · profiles ·
  crossword · spot-six`. `authors` is a list of `taPair`s: the printed Tamil name and the Latin
  spelling of it.
- **`src/content/arivumalar/2026/people/<slug>.yaml`** — one person: first name, `printed_name`,
  city, the labelled fields and panels as printed, both photos, and their closing quote.
- **`taPair`** — Tamil required, English optional, because the magazine has no English titles. The
  shared `pair` type still requires English and is unchanged.

## Deliberately left out

Four page headings the web edition has no use for: `குமரவேல் நாராயணன் — தொடர்ச்சி` (the
continuation folds into one web page), and the puzzle answers' own page titles (the answers sit
behind a button). They are listed in `DROPPED` in the extract script, with the reason.

## What this does not settle

- The reading order. It is the printed order for now, by Saran's decision, and he moves sections
  after reading them on the web.
- Which release-night photograph goes on which profile page. The slot is built and empty; Saran
  tags them from the contact sheet in `/mnt/data/f-section/review/arivumalar-tagging.html`.
- The `அன்று` photos of வைரமுத்து and ஸ்ரீதர், and மோகன்சுகுமார்'s `இன்று` photo: all three are
  cropped from the printed book, which carries reworks made after the design was finished.
- DESIGN.md §3 and §6.3 are updated when the pages are built (checkpoint 3). §10.4 is updated now,
  with the schema.

## Checkpoints

1. **Extract** — done 2026-10-31. 27 reading pages, 19 profiles, 69 photos listed, no text lost.
2. **Proof** — done 2026-10-31. Saran read it and sent three corrections, all applied.
3. **Build on `staging`** — done 2026-10-31, reworked the same evening. 96 pages: the issue page, 27
   reading pages, the profiles index and 19 profile pages, in both languages.
4. **Media** — 71 pictures and the printed book uploaded to R2 on 2026-10-31 with Saran's yes:
   72 objects, 46.0 MiB, `rclone copy --immutable`, nothing overwritten.
5. **Saran reads it on the preview** — first pass 2026-10-31, seven changes, all applied below.
6. **PR → Saran merges**, then the reorder pass and the three photo crops from the printed book.

## The first read on the web (Saran, 2026-10-31, the same evening)

Seven changes after reading it on the preview. They are all about the same thing: the web edition
is not the printed one, and the places where it still behaved like a printed book were the places
that read worst.

1. **`அன்று` is a thumbnail now.** The design export had put those scans in frames the size of a
   modern photograph. They are scans of a page printed 30 years ago, so at that size they showed
   nothing but their own pixels.
2. **Nothing is cropped to a 4:5 box.** Many of the family photographs are wide; the crop was
   cutting people off at both ends — two of them off Saran's own. Every picture is now shown whole,
   and the `அன்றும் இன்றும்` cards letterbox theirs inside the frame so the grid of 19 stays even.
3. **`சொல்ல மறந்த கதை` moved onto the profile pages**, under that heading, and is no longer a page
   of its own. In print it was a spread because the profile pages had no room left; online they do.
   `extract.py` still reads the spread — that is where each person's quote comes from — but no
   longer writes it as a reading page.
4. **The `அன்றும் இன்றும்` cards carry the name alone**, not the city as a subtitle.
5. **The English pages print the magazine's own Tamil titles.** They had been showing nothing but
   the author's name, because `title.en` is empty for every section and the English contents fell
   back to it. Only people's names change language now: the Latin spelling comes from the slug
   already in that person's URL and photo file names. கலைச்செழியன் and மகேந்திரன் have no profile
   page, so no slug and no Latin spelling — their names stay in Tamil until Saran gives one.
6. **The contents sidebar is gone at every width.** A standing list of 27 titles beside the text
   took the eye off the page it was there to serve. The button and the dialog do the same job and
   leave the reading column the screen.
7. **The issue page lost the page count, the editor's line and the note under the download
   button.** The title and the three buttons are the whole of what that page has to say.

`/arivumalar/` also gained its Tamil caption, in Saran's own words.

**And two more, after that pass.** The `அன்று` scans are published as even thumbnails of their own
(`public/arivumalar/2026/then/`, 320×400, 150 KB for all seventeen), not as the 1200px blow-ups the
design exported: trimmed, pulled to one tone, the print screen softened, the same 4:5 frame. The
originals stay in R2, unreferenced; nothing was overwritten. And the names on the
`அன்றும் இன்றும்` cards are in the site's heading face — Caveat on the English pages, Noto Sans
Tamil on the Tamil ones, since Caveat has no Tamil letters.

## Rollback

Everything is new. `git revert` removes the content and the pages, and the R2 keys are all new
under `public/arivumalar/2026/`, so nothing already live changes.
