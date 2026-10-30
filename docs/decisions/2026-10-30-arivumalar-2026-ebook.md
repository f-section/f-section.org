# Arivu Malar 2026 as an online e-book

**Date:** 2026-10-30
**Approved by:** Saran (the four answers below). The rest is a proposal: Claude Code confirms it with Saran at checkpoint 1, before building.
**Affects:** DESIGN.md §3 (site map), §10.4 (Arivu Malar schema); `src/content.config.ts`; `src/pages/[...lang]/arivumalar/`; R2 prefix `public/arivumalar/2026/`

## What changed
The 2026 30th-anniversary Arivu Malar, which was designed page by page in Claude Design and printed for the reunion, gets its own home at `/arivumalar/2026/`. Readers can use it in three ways:

| Mode | URL | What it is | Order |
|---|---|---|---|
| **Read online** (main mode) | `/arivumalar/2026/<section-slug>/` | One web page per section. The text reflows to fit a phone screen. | **Web order**, a new reading order (see Saran's answers) |
| **Book view** | `/arivumalar/2026/book/#p=12` | The printed pages as images. Swipe on a phone; two-page spread on a computer; pinch to zoom. | **Print order**, exactly as printed |
| **Download** | a link on the issue page | One combined PDF of the printed book | Print order |

The issue page `/arivumalar/2026/` shows the front cover, the contents (in web order) and three buttons: "Read", "Book view" and "Download PDF". The existing `/arivumalar/` page links to it.

## Saran's answers (approved 2026-10-30)
1. **Public.** The book is public, and its text may sit in this public repo as Markdown.
2. **Reading order.** The online reading order is different from the printed order. Saran works it out with Claude Code. The book view and the PDF keep the printed order.
3. **Tamil only.** There are no English titles or summaries for now. Menus and buttons still follow the site's language toggle. On both `/arivumalar/2026/…` and `/ta/arivumalar/2026/…`, the magazine text is shown in Tamil.
4. **Interactive puzzles come later.** The crossword (குறுக்கெழுத்துப் போட்டி) and six differences (ஆறு வித்தியாசம்) appear as their printed page images for now.

## Why three modes
- **Most readers are 50+ and on phones.** A Letter-size page on a phone needs pinch-zooming on every line, so the reflowed text is the main way to read.
- **The book view keeps the look of the printed book** that people hold in their hands. It also stays exactly true to print.
- **The PDF** is for people who want to keep or print a copy.

## Source files and what each one is used for
All originals live on minnaham under `/mnt/data/f-section/arivumalar/2026/incoming/`, with a backup copy on the NAS. None of them go into git (CLAUDE.md rules 1 and 13).

| Source | Facts checked on 2026-10-29 | Used for |
|---|---|---|
| `print-ready/*.pdf` | 19 PDFs, **71 pages**, Letter size (612 × 792 pt). Made with "Microsoft: Print To PDF". **They have no text layer:** no fonts, and the text is drawn as shapes. They render sharply at any size, but no text can be extracted. | Page images for the book view, and the combined PDF |
| `print-ready/முன்_அட்டை.png`, `பின்_அட்டை.png` | Front and back covers | Covers in the book view and PDF; the issue page's cover image; link previews |
| Claude Design **Zip export** | Not exported yet. Saran exports it before standalone Claude Design closes on **2026-12-14**. | **The final text** (it includes the edits made during design) and the visual style (fonts, colours, ornaments) |
| `finalized-articles/*.docx` and pictures | The articles as written, before layout | A cross-check of the text, and full-size original photos where a section needs them |

**Where the text comes from, in order of preference:**
1. The Claude Design HTML.
2. If a section is missing there, the `.docx`.
3. OCR of the page images, only as a last resort. Tamil OCR makes many mistakes.

Whichever source is used, Saran proofreads every section against the printed book.

## Content model (proposal)
- **Issue file:** `src/content/arivumalar/2026.yaml`, with `id: "2026"` and `kind: annual` (the existing schema already allows this). Add:
  - `cover`: the R2 key of the front cover
  - `print_pages`: 71, plus the cover pages
  - `pdf`: the R2 key of the combined PDF
  - `book`: the R2 prefix for page images
  - Derive the contents from the sections. Keep `contents` for scanned archive issues only.
- **Sections:** a new collection, one Markdown file per section at `src/content/arivumalar/2026/NN-<slug>.md`. `NN` is the **web order**. Frontmatter:
  ```yaml
  issue: "2026"
  slug: editorial                 # English slug. Saran approves the slugs at checkpoint 1.
  order: 1                        # web reading order
  title: { ta: "ஆசிரியர் நெஞ்சம்" }   # Tamil required, English optional (see note below)
  authors: []                     # first names only, Tamil spelling exactly as Saran gives it
  type: article                   # article | poem | story | humour | photo-feature | pages
  print_pages: [3, 4]             # where the section sits in the printed book
  ```
- **The `type` field sets the layout:**
  - `article`, `story`, `humour`: normal reflowed text.
  - `poem`: keeps every line break exactly as printed.
  - `photo-feature`: text and photos, using the original photos (web copies in R2).
  - `pages`: shows the section's printed page images inline. This is for the puzzles now, and for any section that cannot be reflowed well.
- **Schema note:** the shared `pair` type requires English. Section titles here need **Tamil required, English optional**, so add a `taPair` type for this collection rather than putting placeholder English in.
- **Every section page shows:** the title, the authors, the text with `lang="ta"` and about 1.8 line height, previous/next buttons in web order, and a "see it in the printed book" link to `book/#p=<first print page>`.

## R2 layout (all new keys; nothing existing is touched)
```
public/arivumalar/2026/cover-front.webp, cover-back.webp
public/arivumalar/2026/pages/p001.webp         display, about 1100 px wide
public/arivumalar/2026/pages/p001-zoom.webp    zoom, about 2200 px wide
public/arivumalar/2026/pages/p001-thumb.webp   thumbnail, about 300 px wide
public/arivumalar/2026/img/<slug>-NN.webp      photos used in the reflowed sections
public/arivumalar/2026/arivumalar-2026.pdf     combined, print order
```
- **Page images:** render from the PDFs with `pdftoppm` at about 260 dpi. The PDFs are vector, so this is lossless up to that size. Convert to WebP.
- **Combined PDF:** join the covers and the 19 PDFs in print order (`img2pdf` for the covers, `pdfunite` for the rest). Try a compressed copy with Ghostscript, and keep it only if the text still looks sharp when zoomed in.
- **Upload** with `rclone copy --immutable` and `Cache-Control: public, max-age=31536000, immutable`, the same as videos. Do a dry run first, and get Saran's "yes" before the real upload.
- **Size:** my rough estimate is under 100 MB in total. The bucket currently holds about 150 MiB of the 10 GB free tier.

## Checkpoints (Saran approves each one before the next step)
1. **Inventory and order (read only).** Unzip the Claude Design export into a working folder. List each section and match its HTML, print PDF, `.docx` and print page numbers. Pull out the fonts and colours. Propose the slugs, the web order and the `type` of each section. Saran settles the web order here.
2. **Page images and PDF.** Build them locally, show a few sample pages and the PDF size, then upload after a "yes".
3. **Text.** Extract every section to Markdown and list each place where the HTML and the `.docx` differ. Saran proofreads one section at a time. Claude Code does not change Tamil wording, spelling, punctuation or names on its own.
4. **Pages.** Build the issue page, section pages, book viewer and download, on `staging`. Saran checks them on a phone over mobile data, then merges.

## Not now
- English titles and summaries.
- Interactive crossword and six differences.
- EPUB download.
- Search inside the magazine.
- The scanned 1992–96 archive issues. They will reuse the same book viewer later.

## Rollback
Everything here is new. The new pages and content can be removed with `git revert`, and the R2 keys are new keys under `public/arivumalar/2026/`, so nothing that is already live changes.
