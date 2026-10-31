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
| Names | the book's full names | **first names only** (rule 14), with `printed_name` keeping what the book printed. |

## The shape

| URL | What it is |
|---|---|
| `/arivumalar/` | What Arivu Malar is, a card for the 2026 issue, a note that the 1992–96 archive comes later |
| `/arivumalar/2026/` | The issue page: front cover, **பொருளடக்கம்**, **முகப்பு** into the book, **தரவிறக்கம் · 39.5 MB** |
| `/arivumalar/2026/<slug>/` | One reading page per section, 27 of them |
| `/arivumalar/2026/people/` | The `அன்றும் இன்றும்` index: 19 names with their `இன்று` photo |
| `/arivumalar/2026/people/<name>/` | One page per person — **`noindex`** |

The `/ta/` mirror carries the same pages; the chrome follows the language toggle and the magazine
text is Tamil on both, since there are no English titles for now.

**Reading UI.** A sticky contents sidebar from 1024px up, with the current section marked. On a
phone a **பொருளடக்கம்** button in the page header opens the contents over the page — the same
native `<dialog>` as the Lightbox, so no new dependency. Each section ends with prev · next in the
configured order and a link back to the issue page.

**Typography.** 18px Noto Sans Tamil, 1.8 line height, a ~34em measure, paper/ink/ink-red. The A5
design is not reproduced: at 8.2pt a scaled A5 page lands near 6px on a phone, which rule 7 rules
out. The printed look lives in the PDF.

**Photos** run inline where the design placed them — floated beside the text on a computer, full
width above it on a phone — and tap into the existing Lightbox. The design's floats are in mm and
are not carried over.

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
  quotes · crossword · spot-six`.
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
- Alt text for 24 photos that the print design needed none for, including the four கான்ஸ்டன்
  pictures whose captions the design hand-over left open.
- The `அன்று` photos of வைரமுத்து and ஸ்ரீதர், and மோகன்சுகுமார்'s `இன்று` photo: all three are
  cropped from the printed book, which carries reworks made after the design was finished.
- The two short untitled poems printed inside குமாரவேல்'s own profile page: left on his page for
  now.
- DESIGN.md §3 and §6.3 are updated when the pages are built (checkpoint 3). §10.4 is updated now,
  with the schema.

## Checkpoints

1. **Extract** — done 2026-10-31. 27 reading pages, 19 profiles, 69 photos listed, no text lost.
2. **Proof** — Saran reads it section by section; the three photo crops from the printed book.
3. **Build on `staging`** — issue page, sections, profiles, contents panel, puzzles, prev/next.
4. **Media** — convert, dry-run the upload, Saran's yes, upload.
5. **PR → Saran merges**, then the reorder pass.

## Rollback

Everything is new. `git revert` removes the content and the pages, and the R2 keys are all new
under `public/arivumalar/2026/`, so nothing already live changes.
