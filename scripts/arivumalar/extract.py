"""Pull the Arivu Malar 2026 e-book out of the Claude Design export into content files.

Dry run is the default: it only prints what it found. Pass --apply to write files.

The export's `.dc.html` files hold the finished print design with the Tamil text live in
the markup, so nothing here is OCR'd, retyped or translated. Every string is copied
byte for byte out of the HTML; this script only decides which block is a heading, a
paragraph, a poem line, a pull-quote, a byline or a photo.

Rules (CLAUDE.md, and the export's own CLAUDE.md):
  * Never rewrite, trim or "fix" Tamil text. Text is copied verbatim.
  * `uploads/அறிவுமலர் - நினைவுகள்.json` is NOT read: it carries email addresses and
    Google Drive links (rule 10), it covers only the first 14 people, and its answers
    predate the edits made during design. The printed HTML is the authority.
  * People are named by first name only on the website (rule 14). The book prints full
    names, so the first names live in NAMES below, for Saran to check.
  * Images are only listed here. Converting and uploading them is a separate step.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_SECTIONS = REPO / "src" / "content" / "arivumalar" / "2026" / "sections"
OUT_PEOPLE = REPO / "src" / "content" / "arivumalar" / "2026" / "people"
DEFAULT_SRC = Path(
    "/mnt/data/f-section/arivumalar/2026/incoming/claude-design-arivumalar-source/design"
)

VOID = {"img", "br", "meta", "link", "hr", "input", "source", "col"}
SKIP = {"script", "style", "helmet", "head"}
# Text inside these belongs to the block around them, not to a block of their own.
INLINE = {"span", "b", "strong", "em", "i", "u", "a", "sup", "sub", "small", "code", "mark"}
# Design-runtime wrappers: keep the children, drop the element.
TRANSPARENT = {"x-dc", "doc-page", "sc-if", "sc-for", "html", "body", "tbody"}


# --------------------------------------------------------------------------- tiny DOM


@dataclass
class Node:
    tag: str = ""
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node"] = field(default_factory=list)
    text: str | None = None  # set on text nodes only

    @property
    def is_text(self) -> bool:
        return self.text is not None


class Tree(HTMLParser):
    """Builds a Node tree. `<br>` becomes a newline so poem lines survive."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.root = Node(tag="#root")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            self.stack[-1].children.append(Node(text="\n"))
            return
        node = Node(tag=tag, attrs={k: (v or "") for k, v in attrs})
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(Node(text=data))

    def handle_entityref(self, name: str) -> None:
        self.stack[-1].children.append(Node(text=html.unescape(f"&{name};")))

    def handle_charref(self, name: str) -> None:
        self.stack[-1].children.append(Node(text=html.unescape(f"&#{name};")))


def parse(path: Path) -> Node:
    t = Tree()
    t.feed(path.read_text(encoding="utf-8"))
    return t.root


def find(node: Node, pred, out: list[Node] | None = None) -> list[Node]:
    out = [] if out is None else out
    if not node.is_text:
        if pred(node):
            out.append(node)
        for c in node.children:
            find(c, pred, out)
    return out


# --------------------------------------------------------------------------- styles


def style_of(node: Node) -> dict[str, str]:
    raw = node.attrs.get("style", "")
    out: dict[str, str] = {}
    for part in raw.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


INHERITED = ("font-family", "font-size", "color", "text-align", "letter-spacing", "text-transform")


def merged(parent: dict[str, str], own: dict[str, str]) -> dict[str, str]:
    s = {k: v for k, v in parent.items() if k in INHERITED}
    s.update(own)
    return s


def pt(value: str | None) -> float:
    """Font size in points. mm and px are converted roughly, only for comparing."""
    if not value:
        return 0.0
    m = re.match(r"([\d.]+)\s*(pt|px|mm|em)?", value)
    if not m:
        return 0.0
    n = float(m.group(1))
    unit = m.group(2) or "px"
    return {"pt": n, "px": n * 0.75, "mm": n * 2.835, "em": n * 8.0}[unit]


# --------------------------------------------------------------------------- blocks


@dataclass
class Block:
    kind: str
    text: str = ""
    src: str = ""
    alt: str = ""
    size: float = 0.0
    align: str = ""
    color: str = ""
    family: str = ""
    spacing: str = ""
    # Where this block sat in the markup. Poem lines of one stanza share a parent,
    # because the design wraps each stanza in its own div.
    parent: str = ""

    def as_dict(self) -> dict:
        d = {"kind": self.kind}
        for k in ("text", "src", "alt", "align", "color", "spacing"):
            if getattr(self, k):
                d[k] = getattr(self, k)
        if self.size:
            d["size"] = round(self.size, 1)
        if self.family:
            d["family"] = self.family
        return d


def inline_text(node: Node) -> str:
    """Text that belongs to this block: its own text plus any inline descendants'."""
    out: list[str] = []

    def rec(n: Node) -> None:
        for c in n.children:
            if c.is_text:
                out.append(c.text or "")
            elif c.tag in INLINE:
                rec(c)

    rec(node)
    return "".join(out)


def tidy(text: str) -> str:
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return "\n".join(lines).strip("\n ")


def family_of(style: dict[str, str]) -> str:
    fam = style.get("font-family", "")
    for name in ("Baloo", "Figtree", "Noto Serif Tamil"):
        if name in fam:
            return name
    return ""


def classify(node: Node, style: dict[str, str], text: str) -> str:
    fam = family_of(style)
    size = pt(style.get("font-size"))
    align = style.get("text-align", "")
    upper = style.get("text-transform", "") == "uppercase"
    if node.tag in ("h1", "h2", "h3", "h4", "h5"):
        return "heading"
    if fam == "Figtree" and upper:
        return "label"
    # Folio and running head: small Figtree, not centred, repeating the section title.
    if fam == "Figtree" and size and size <= 8 and align != "center":
        return "furniture"
    if fam == "Figtree":
        return "label"
    if text.lstrip().startswith(("~", "–", "—")) and (align == "right" or fam == "Baloo"):
        return "byline"
    if fam == "Baloo" and align == "center":
        return "pullquote"
    if fam == "Baloo" and size >= 11:
        return "heading"
    if fam == "Baloo":
        return "pullquote"
    return "text"


def blocks_of(node: Node, inherited: dict[str, str] | None = None, path: str = "") -> list[Block]:
    """Every visible run of text and every image, in document order."""
    out: list[Block] = []
    style = merged(inherited or {}, style_of(node))
    parent = path.rsplit(".", 1)[0] if "." in path else ""

    if node.tag == "img":
        out.append(
            Block(
                kind="image",
                src=node.attrs.get("src", ""),
                alt=tidy(html.unescape(node.attrs.get("alt", ""))),
                parent=parent,
            )
        )
        return out

    own = tidy(html.unescape(inline_text(node)))
    if own:
        out.append(
            Block(
                kind=classify(node, style, own),
                text=own,
                size=pt(style.get("font-size")),
                align=style.get("text-align", ""),
                color=style.get("color", "").lower(),
                family=family_of(style),
                spacing=style.get("letter-spacing", ""),
                parent=parent,
            )
        )

    for i, c in enumerate(node.children):
        if c.is_text or c.tag in SKIP or c.tag in INLINE:
            continue
        out.extend(blocks_of(c, style, f"{path}.{i}" if path else str(i)))
    return out


def is_sage_note(b: Block) -> bool:
    """The small sage-green line under a game's heading: an instruction, not body text."""
    return b.kind == "text" and b.color == "#56633f" and 0 < b.size <= 8


def pages_of(root: Node) -> list[tuple[str, Node]]:
    """(label, node) for every printed page in a design file."""
    sections = find(root, lambda n: n.tag == "section" and "page" in n.attrs.get("class", ""))
    pages = [(n.attrs.get("data-screen-label", ""), n) for n in sections]
    if pages:
        return pages
    # The covers are plain artboard divs, not doc-page sections.
    boards = find(root, lambda n: n.tag == "div" and n.attrs.get("data-artboard-id"))
    return [(n.attrs.get("data-artboard-id", ""), n) for n in boards]


# --------------------------------------------------------------------------- the book

# First names only on the website (rule 14). Left side is exactly what the book prints,
# right side is what the site shows. Saran checks this table; nothing here is guessed
# beyond dropping initials and surnames.
NAMES = {
    "வி. கணேஷ்": "கணேஷ்",
    "கான்ஸ்டன்": "கான்ஸ்டன்",
    "குமரவேல் நாராயணன்": "குமாரவேல்",
    "குமரவேல்": "குமாரவேல்",
    "குமாரவேல்": "குமாரவேல்",
    "சரவணன்": "சரவணன்",
    "ஆர். சீனிவாசன்": "சீனிவாசன்",
    "ஆர். சுகந்தி": "சுகந்தி",
    "செந்தமிழ்ச் செல்வன் சு.": "செந்தமிழ்ச் செல்வன்",
    "பரிணீதா": "பரிணீதா",
    "வி. என். பாஞ்சாலை": "பாஞ்சாலை",
    "புவனேஷ் சுப்ரமணியன்": "புவனேஷ்",
    "புவனேஷ்": "புவனேஷ்",
    "டி. மணிகண்டன்": "மணிகண்டன்",
    "மரகதவல்லி": "மரகதவல்லி",
    "முகமது இஸ்மாயில்": "இஸ்மாயில்",
    # Some Tamil first names run to two words, with the surname separate (Saran,
    # 2026-10-31). மோகன் சுகுமார் and இரமேஷ் கண்ணன் are first names, not name + surname.
    "மோகன்சுகுமார்": "மோகன் சுகுமார்",
    "மோகன் சுகுமார்": "மோகன் சுகுமார்",
    "பி. மோகன்ராஜ்": "மோகன்ராஜ்",
    "எம். ரமேஷ் கண்ணன்": "இரமேஷ் கண்ணன்",
    "சி ராம்மோகன்": "ராம்மோகன்",
    "சி. ராம்மோகன்": "ராம்மோகன்",
    "வைரமுத்து டி.": "வைரமுத்து",
    "ஸ்ரீதர் டி.": "ஸ்ரீதர்",
    "கலைச்செழியன்": "கலைச்செழியன்",
    "மகேந்திரன்": "மகேந்திரன்",
}

# ASCII slug per person, matching the photo filenames the design already uses.
PEOPLE_SLUGS = {
    "கணேஷ்": "ganesh",
    "கான்ஸ்டன்": "constan",
    "குமாரவேல்": "kumaravel",
    "சரவணன்": "saravanan",
    "சீனிவாசன்": "srinivasan",
    "சுகந்தி": "suganthi",
    "செந்தமிழ்ச் செல்வன்": "senthamilselvan",
    "பரிணீதா": "parineetha",
    "பாஞ்சாலை": "panchalai",
    "புவனேஷ்": "bhuvanesh",
    "மணிகண்டன்": "manikandan",
    "மரகதவல்லி": "maragathavalli",
    "இஸ்மாயில்": "ismail",
    "மோகன் சுகுமார்": "mohan-sugumar",
    "மோகன்ராஜ்": "mohanraj",
    "இரமேஷ் கண்ணன்": "ramesh-kannan",
    "ராம்மோகன்": "rammohan",
    "வைரமுத்து": "vairamuthu",
    "ஸ்ரீதர்": "sridhar",
}


# The Latin spelling for someone with no profile page, and so no slug to take it from.
# Both of these are Saran's own (2026-10-31); Claude never invents a spelling of a
# friend's name (rule 14).
ENGLISH_NAMES = {
    "கலைச்செழியன்": "Kalaichezhian",
    "மகேந்திரன்": "Mahendran",
}


def english_name(first: str) -> str:
    """
    The Latin spelling of a first name: the slug Saran approved for the URLs and the
    photo file names, in title case, or ENGLISH_NAMES where there is no slug.
    """
    if first in ENGLISH_NAMES:
        return ENGLISH_NAMES[first]
    slug = PEOPLE_SLUGS.get(first)
    return slug.replace("-", " ").title() if slug else first


def name_pair(printed: str) -> dict:
    """`{ta, en}` for a name as the book printed it."""
    first = NAMES.get(printed, printed)
    return {"ta": first, "en": english_name(first)}


@dataclass(frozen=True)
class Sec:
    """One reading page of the web edition, and where it comes from in the export."""

    slug: str
    source: str
    type: str
    authors: tuple[str, ...] = ()
    pages: tuple[int, ...] = ()  # 1-based pages of the design file; empty means all
    title: str = ""  # only when the design heading is not the title we want
    start: str = ""  # take blocks from the one whose text starts with this
    stop: str = ""  # ...up to the one whose text starts with this
    take: tuple[int, ...] = ()  # keep only these text blocks of the region, in this order
    dark: bool = False
    page: bool = True  # False: read for what it feeds, but not written as a reading page


POEMS = "கவிதைகள்.dc.html"
SPOT = "வித்தியாசங்களைக் கண்டுபிடி.dc.html"
PROFILES = "அன்றும் இன்றும்.dc.html"

SECTIONS = (
    Sec("inside-cover-1995", "உள் அட்டை - 1995.dc.html", "scans", title="அறிவு மலர் · 1995"),
    Sec("editors-note", "ஆசிரியர் நெஞ்சம்.dc.html", "article"),
    Sec("f-section-timeless", "கட்டுரை - காலத்தால் அழியாத F பிரிவு - இஸ்மாயில்.dc.html", "article", ("இஸ்மாயில்",)),
    Sec("natpu", POEMS, "poem", ("மோகன்சுகுமார்",), pages=(1,)),
    Sec("memories-that-never-fade", "நினைவலைகள் - பரிணீதா.dc.html", "memoir", ("பரிணீதா",)),
    Sec("unchanging-people", POEMS, "poem", ("குமாரவேல்",), pages=(5,)),
    Sec("tamil-in-ai", "கட்டுரை - செயற்கை நுண்ணறிவில் தமிழ் - சரவணன்.dc.html", "article", ("சரவணன்",)),
    Sec("thavam", POEMS, "poem", ("குமாரவேல்",), pages=(6,)),
    Sec("from-the-sea-to-life", "கடலிலிருந்து வாழ்க்கைக்கு - கான்ஸ்டன்.dc.html", "memoir", ("கான்ஸ்டன்",)),
    Sec(
        "shadows-still-talking",
        PROFILES,
        "poem",
        ("குமாரவேல்",),
        pages=(4,),
        start="கவிதைகள்",
        take=(0, 1),
        title="நிழல்கள் · நீயிருக்கும் வகுப்பறை",
    ),
    Sec("olithu-kol", "கதை - ஒலித்து கொல் - பாஞ்சாலை.dc.html", "story", ("பாஞ்சாலை",)),
    Sec("spot-six", SPOT, "spot-six", title="ஆறு வித்தியாசங்களைக் கண்டுபிடி", stop="கவிதை"),
    Sec("you-can-do-it", "கதை - உன்னால் முடியும் தம்பி - மோகன் சுகுமார்.dc.html", "story", ("மோகன்சுகுமார்",)),
    Sec("breathing-distance", SPOT, "poem", ("குமாரவேல்",), pages=(2,), start="கவிதை", stop="விளையாட்டு · விடைகள்"),
    Sec("tamils-in-the-uae", "கட்டுரை - அமீரக வளர்ச்சியில் தமிழர் தடம் - புவனேஷ்.dc.html", "article", ("புவனேஷ்",)),
    Sec("aval", POEMS, "poem", ("கலைச்செழியன்",), pages=(2,)),
    Sec("crossword", "குறுக்கெழுத்துப் போட்டி.dc.html", "crossword"),
    Sec("why-this-alphabet-order", "கட்டுரை - வரிசையில் என்ன உள்ளது - சரவணன்.dc.html", "article", ("சரவணன்",)),
    Sec("my-poem-has-not-aged", POEMS, "poem", ("குமாரவேல்",), pages=(3, 4)),
    Sec("indian-steel-industry", "கட்டுரை - இந்தியாவின் எஃகு தொழில் - செந்தமிழ்ச் செல்வன்.dc.html", "article", ("செந்தமிழ்ச் செல்வன்",)),
    Sec("whatsapp-group", POEMS, "poem", ("குமாரவேல்",), pages=(7,)),
    Sec("humour", "நகைச்சுவை(யா).dc.html", "humour"),
    Sec("those-four-years", "1992-96 அந்த நான்கு ஆண்டுகள்.dc.html", "photos"),
    Sec("twenty-years-on", "2016 இருபது ஆண்டுகளுக்குப் பின்.dc.html", "photos"),
    Sec("the-addressless", POEMS, "poem", ("மகேந்திரன்",), pages=(9,), dark=True),
    Sec("then-and-now", PROFILES, "profiles", title="அன்றும் இன்றும்", pages=()),
    # Not a page of the web edition (Saran, 2026-10-31). In print these closing words
    # were pulled out into a spread of their own for want of room on the profile pages;
    # online there is room, so each one is read here and printed on its own profile.
    Sec("the-untold-story", PROFILES, "quotes", title="சொல்ல மறந்த கதை", pages=(21, 22), page=False),
    Sec("f-section-vairamuthu", "F Section - வைரமுத்து.dc.html", "article", ("வைரமுத்து",), title="F Section"),
)


# --------------------------------------------------------------------------- writing


# The 1996 portraits are published as even thumbnails, not as the 1200px scans the
# design scaled them up to (Saran, 2026-10-31); media.py makes them, and they get a
# prefix of their own so nothing in R2 is overwritten.
THEN_SRC = "assets/family/old/"

# Three 1996 portraits the design export never had (Saran, 2026-11-02): he cropped them
# out of the printed book himself. They sit beside the export, not in it, so the export
# stays exactly as Claude Design wrote it. மோகன் சுகுமார் had a scan already; his crop
# replaces it, under its own key, so nothing in R2 is overwritten.
CROP_SRC = "crops/"
THEN_CROPS = {
    "மோகன் சுகுமார்": "crops/mohan-sugumar.jpg",
    "வைரமுத்து": "crops/vairamuthu.jpg",
    "ஸ்ரீதர்": "crops/sridhar.jpg",
}


def then_key(src: str) -> str:
    """`assets/family/old/constan.png` -> `public/arivumalar/2026/then/constan.webp`"""
    bare = src.removeprefix(THEN_SRC).removeprefix(CROP_SRC)
    stem = re.sub(r"\.[a-z]+$", "", bare, flags=re.I)
    return f"public/arivumalar/2026/then/{re.sub(r'[^a-z0-9]+', '-', stem.lower()).strip('-')}.webp"


def flat_key(src: str) -> str:
    """`assets/family/old/constan.png` -> `public/arivumalar/2026/img/family-old-constan.webp`"""
    stem = re.sub(r"\.[a-z]+$", "", src, flags=re.I)
    stem = re.sub(r"^(assets|uploads)/", "", stem)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", stem).strip("-").lower()
    return f"public/arivumalar/2026/img/{slug}.webp"


def md_image(b: Block) -> tuple[dict, str]:
    """A photo in the body. The `r2:` scheme keeps Astro's image pipeline out of it:
    the page turns it into a media.f-section.org URL when it renders."""
    key = flat_key(b.src)
    return {"key": key, "source": b.src, "alt": b.alt}, f"![{b.alt}](r2:{key})"


def md_lines(text: str) -> str:
    """Keep the printed line breaks: a backslash is a hard break in Markdown."""
    lines = text.split("\n")
    return "\\\n".join(lines)


def pick(blocks: list[Block], sec: Sec) -> list[Block]:
    out = blocks
    if sec.start:
        for i, b in enumerate(out):
            if b.text.startswith(sec.start):
                out = out[i:]
                break
    if sec.stop:
        for i, b in enumerate(out):
            if i and b.text.startswith(sec.stop):
                out = out[:i]
                break
    if sec.take:
        texts = [b for b in out if b.kind == "text"]
        out = [texts[i] for i in sec.take if i < len(texts)]
    return out


def section_pages(path: Path, sec: Sec) -> list[list[Block]]:
    pages = pages_of(parse(path))
    chosen = [pages[i - 1] for i in sec.pages] if sec.pages else pages
    return [pick(blocks_of(node), sec) for _, node in chosen]


def write_prose(sec: Sec, pages: list[list[Block]]) -> tuple[dict, str]:
    """Articles, memoirs, stories: headings, paragraphs, quotes and photos in order."""
    meta: dict = {}
    body: list[str] = []
    photos: list[dict] = []
    title = ""
    title_open = False  # the title's second line, if it has one, comes straight after
    for blocks in pages:
        for i, b in enumerate(blocks):
            prev = blocks[i - 1] if i else None
            if b.kind == "furniture":
                continue
            if b.kind == "heading":
                one_line = " ".join(b.text.split("\n"))
                if not title and b.size >= 13:
                    title, title_open = one_line, True
                    continue
                # A long title splits in two: line 2 is sage and right-aligned (PRINT-RULES).
                if title_open and b.color == "#56633f" and b.align == "right":
                    title = f"{title} {one_line}"
                    continue
                title_open = False
                body.append(f"## {md_lines(b.text)}")
                continue
            if b.kind == "label":
                if not meta.get("kicker") and b.spacing in (".22em", ".28em") and b.align != "center":
                    meta["kicker"] = b.text
                    continue
                # The author line under the title, as printed (it may carry a city too).
                if not body and b.color == "#56633f" and b.spacing == ".16em":
                    meta["byline"] = b.text
                    title_open = False
                    continue
                # A small centred label under a quote is that quote's attribution.
                if prev and prev.kind == "pullquote" and body:
                    body[-1] = f"{body[-1]}\n>\n> — {b.text}"
                    continue
                body.append(f"**{b.text}**")
                continue
            if b.kind == "pullquote":
                body.append("\n".join(f"> {ln}" for ln in b.text.split("\n")))
                continue
            if b.kind == "byline":
                body.append(f"*{b.text}*")
                continue
            if b.kind == "image":
                photo, md = md_image(b)
                photos.append(photo)
                body.append(md)
                continue
            # The quieter line printed directly under a quote belongs to it.
            if prev and prev.kind == "pullquote" and b.align == "center" and body:
                body[-1] = f"{body[-1]}\n>\n" + "\n".join(f"> {ln}" for ln in b.text.split("\n"))
                continue
            body.append(md_lines(b.text))
    meta["title"] = {"ta": sec.title or title}
    if photos:
        meta["photos"] = photos
    return meta, "\n\n".join(body)


def write_poem(sec: Sec, pages: list[list[Block]]) -> tuple[dict, str]:
    """One poem. Every printed line break is kept; stanzas stay separate paragraphs."""
    meta: dict = {}
    body: list[str] = []
    title = ""
    dedication = ""
    note = ""
    photos: list[dict] = []
    stanza: list[str] = []
    at: tuple[str, str, float] | None = None

    def flush() -> None:
        nonlocal stanza
        if stanza:
            body.append("\\\n".join(stanza))
            stanza = []

    for blocks in pages:
        for b in blocks:
            if b.kind in ("furniture", "byline"):
                continue
            if b.kind == "image":
                flush()
                photo, md = md_image(b)
                photos.append(photo)
                body.append(md)
                continue
            if b.kind == "heading":
                flush()
                if b.text == "கவிதைகள்":  # the collection's masthead, not this poem's title
                    continue
                if not title:
                    title = " ".join(b.text.split("\n"))
                continue
            if b.kind == "label":
                flush()
                if not meta.get("kicker"):
                    meta["kicker"] = b.text
                continue
            # The small grey line after a poem: where it was written or what it won.
            if (body or stanza) and b.color == "#645c50" and 0 < b.size < 8:
                flush()
                note = b.text
                continue
            if sec.take:
                body.append(md_lines(b.text))
                continue
            if not title:
                dedication = b.text
                continue
            # The design wraps each stanza in its own div, so lines that share a
            # parent are one stanza. A change of colour or size also starts one.
            here = (b.parent, b.color, b.size)
            if at is not None and here != at:
                flush()
            at = here
            stanza.append(md_lines(b.text))
    flush()
    meta["title"] = {"ta": sec.title or title}
    if dedication:
        meta["dedication"] = dedication
    if note:
        meta["note"] = note
    if photos:
        meta["photos"] = photos
    if sec.dark:
        meta["dark"] = True
    # Two short poems on one page: a thematic break between them, no inner heading,
    # because the second poem's first line is also its title (Saran, 2026-10-31).
    joiner = "\n\n***\n\n" if len(sec.take) > 1 else "\n\n"
    return meta, joiner.join(body)


def write_photos(sec: Sec, pages: list[list[Block]]) -> tuple[dict, str]:
    """A photo spread, or the two photographed 1995 pages: pictures with captions."""
    photos: list[dict] = []
    title = ""
    pending: dict | None = None
    for blocks in pages:
        for b in blocks:
            if b.kind == "image":
                pending = {"key": flat_key(b.src), "source": b.src, "alt": b.alt}
                photos.append(pending)
            elif b.kind == "pullquote" and pending is not None:
                pending["caption"] = b.text
                pending = None
            elif b.kind == "heading" and not title:
                title = b.text
    return {"title": {"ta": sec.title or title}, "photos": photos}, ""


def write_humour(sec: Sec, pages: list[list[Block]]) -> tuple[dict, str]:
    jokes: list[dict] = []
    title = ""
    for blocks in pages:
        for b in blocks:
            if b.kind == "heading" and not title:
                title = b.text
            elif b.kind == "text" and b.color == "#645c50":
                jokes.append({"setup": b.text, "lines": []})
            elif b.kind == "pullquote":
                cur = jokes[-1] if jokes else None
                # Two speakers alternate within a joke; the next joke starts when the
                # first speaker's name changes. A setup line has already opened one.
                first = cur["lines"][0]["speaker"] if cur and cur["lines"] else None
                if cur is None or (b.color == "#8c491a" and cur["lines"] and b.text != first):
                    jokes.append({"lines": []})
                jokes[-1]["lines"].append({"speaker": b.text, "text": ""})
            elif b.kind == "text" and jokes and jokes[-1]["lines"]:
                jokes[-1]["lines"][-1]["text"] = b.text
    return {"title": {"ta": sec.title or title}, "jokes": jokes}, ""


def write_crossword(sec: Sec, path: Path) -> tuple[dict, str]:
    """The grid and the clues live in the design file's own script, as JS consts."""
    src = path.read_text(encoding="utf-8")

    def const(name: str) -> str:
        m = re.search(rf"const {name} = (.+?);\n", src, re.S)
        if not m:
            raise SystemExit(f"{path.name}: const {name} not found")
        return m.group(1)

    grid = [row.split("|") for row in json.loads(const("GRID")).split("/")]
    nums = [row.split("|") for row in json.loads(const("NUMS")).split("/")]
    clues = {}
    for key, name in (("across", "ACROSS"), ("down", "DOWN")):
        raw = const(name).replace("[[", "[ [").replace("]]", "] ]")
        clues[key] = [
            {"n": int(n), "answer": a, "clue": c}
            for n, a, c in json.loads(raw.replace("\n", ""))
        ]
    pages = pages_of(parse(path))
    blocks = blocks_of(pages[0][1])
    title = next((b.text for b in blocks if b.kind == "heading"), "")
    note = next((b.text for b in blocks if is_sage_note(b)), "")
    meta = {
        "title": {"ta": sec.title or title},
        "kicker": next((b.text for b in blocks if b.kind == "label"), ""),
        "note": note,
        "grid": ["|".join(r) for r in grid],
        "numbers": ["|".join(r) for r in nums],
        "across": clues["across"],
        "down": clues["down"],
    }
    return meta, ""


def write_spot_six(sec: Sec, pages: list[list[Block]]) -> tuple[dict, str]:
    meta: dict = {"photos": [], "answers": []}
    title = ""
    for blocks in pages:
        for b in blocks:
            if b.kind == "heading" and not title:
                title = b.text
            elif b.kind == "label" and not meta.get("kicker"):
                meta["kicker"] = b.text
            elif is_sage_note(b):
                meta["note"] = b.text
            elif b.kind == "image":
                entry = {"key": flat_key(b.src), "source": b.src, "alt": b.alt}
                if "crop" in b.src:
                    meta["answer_photo"] = entry
                else:
                    meta["photos"].append(entry)
            elif b.kind == "text" and (m := re.match(r"^(\d+)(.+)$", b.text, re.S)):
                meta["answers"].append({"n": int(m.group(1)), "text": m.group(2)})
    meta = {"title": {"ta": sec.title or title}, **meta}
    return meta, ""


def write_quotes(sec: Sec, pages: list[list[Block]]) -> tuple[dict, str]:
    quotes: list[dict] = []
    title = ""
    for blocks in pages:
        for b in blocks:
            if b.kind == "heading" and not title:
                title = b.text
            # Most are plain text; வைரமுத்து's is set as a centred slogan instead.
            elif b.kind in ("text", "pullquote") and b.color == "#2e2b25":
                quotes.append({"text": b.text, "by": ""})
            elif b.kind == "byline" and quotes and not quotes[-1]["by"]:
                printed = b.text.lstrip("—– ").strip()
                quotes[-1]["by"] = NAMES.get(printed, printed)
                quotes[-1]["printed_by"] = printed
    return {"title": {"ta": sec.title or title}, "quotes": quotes}, ""


def write_people(path: Path) -> list[dict]:
    """One record per person. A `— தொடர்ச்சி` page folds back into the person before it."""
    people: list[dict] = []
    for label, node in pages_of(parse(path)):
        if "சொல்ல மறந்த கதை" in label:
            continue
        blocks = blocks_of(node)
        carry_on = "தொடர்ச்சி" in label
        if carry_on:
            if not people:
                raise SystemExit(f"{path.name}: continuation page {label!r} with nobody before it")
            person = people[-1]
        else:
            person = {
                "slug": "",
                "name": {},
                "printed_name": "",
                "order": 0,
                "city": "",
                "fields": [],
                "panels": [],
            }
            people.append(person)

        pending_label = ""
        pending_panel = ""
        in_poems = False
        photo_slot = ""
        for b in blocks:
            if b.kind == "furniture":
                continue
            if b.kind == "heading":
                if carry_on and b.text == "கவிதைகள்":
                    in_poems = True
                elif not person["printed_name"]:
                    person["printed_name"] = b.text
                continue
            if b.kind == "image":
                photo_slot = b.src
                continue
            if b.kind == "label":
                if b.text in ("அன்று", "இன்று") and photo_slot:
                    key = "photo_then" if b.text == "அன்று" else "photo_now"
                    where = then_key if photo_slot.startswith(THEN_SRC) else flat_key
                    person[key] = {"key": where(photo_slot), "source": photo_slot}
                    photo_slot = ""
                elif b.text == "அன்றும் இன்றும்":
                    pass  # the kicker
                elif in_poems:
                    pass  # the poems' byline, already known from the heading
                else:
                    pending_label = b.text
                continue
            if b.kind == "pullquote":
                if b.text.strip().isdigit():
                    person["order"] = int(b.text)
                else:
                    pending_panel = b.text
                continue
            if b.kind == "text":
                if in_poems:
                    continue  # scattered as their own poem pages instead
                if pending_panel:
                    person["panels"].append({"label": pending_panel, "value": b.text})
                    pending_panel = ""
                elif pending_label:
                    person["fields"].append({"label": pending_label, "value": b.text})
                    pending_label = ""
                elif not person["city"]:
                    person["city"] = b.text
            # anything else is decoration

    for p in people:
        printed = p["printed_name"]
        first = NAMES.get(printed)
        if not first:
            raise SystemExit(f"no first name for {printed!r} — add it to NAMES")
        slug = PEOPLE_SLUGS.get(first)
        if not slug:
            raise SystemExit(f"no slug for {first!r} — add it to PEOPLE_SLUGS")
        p["slug"] = slug
        p["name"] = {"ta": first, "en": english_name(first)}
        crop = THEN_CROPS.get(first)
        if crop:
            p["photo_then"] = {"key": then_key(crop), "source": crop}
        for key in ("photo_then", "photo_now"):
            if key in p:
                p[key]["alt"] = f"{first} — {'அன்று' if key == 'photo_then' else 'இன்று'}"
    return people


# --------------------------------------------------------------------------- cli


# A person record, in the order the fields are written out. `photo_event` is the
# reunion photograph of them speaking; Saran tags it by hand, so a re-run keeps it.
PERSON_KEYS = (
    "slug",
    "name",
    "printed_name",
    "order",
    "city",
    "fields",
    "panels",
    "photo_then",
    "photo_event",
    "photo_now",
    "quote",
)


def person_file(p: dict, path: Path) -> dict:
    """The record to write, keeping anything hand-added that this script cannot know."""
    import yaml

    if path.is_file():
        old = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if old.get("photo_event"):
            p = {**p, "photo_event": old["photo_event"]}
    ordered = {k: p[k] for k in PERSON_KEYS if k in p}
    ordered.update({k: v for k, v in p.items() if k not in ordered})
    return ordered


# What kind of piece a reading page is, in the word the printed book used. The book put
# one over most of the prose and nothing over the poems; online every poem says கவிதை
# the way the stories say கதை (Saran, 2026-11-02). It is the same word on every page of
# a kind, and nothing else: the first pass kept a second word the print carried there --
# நினைவஞ்சலி over the tribute, தொகுப்பு over the collected poems -- and reading the
# pages one after another, those read as different kinds of piece (Saran, 2026-11-03).
KINDS = {"poem": "கவிதை", "story": "கதை", "article": "கட்டுரை", "memoir": "கட்டுரை"}
ISSUE_KICKER = "அறிவு மலர் 2026"


def kicker_for(kind: str, printed: str) -> str:
    word = KINDS.get(kind)
    if not word:
        return printed  # the puzzles and the picture spreads keep the book's own line
    return f"{word} · {ISSUE_KICKER}"


# The reading page carries the pictures alone, without the line the book printed under
# them (Saran, 2026-11-03): a caption sat between a picture and the text that should be
# running on beside it. The words are not lost -- a picture the export gave no
# description of takes its caption as its alt text, which is also what the viewer reads
# out. The heading already names the author, so where the book repeated the byline at
# the top of the piece, that goes too; only one name stands over a piece.
CAPTION = re.compile(r"\*\*([^*\n]+)\*\*")
BARE_IMAGE = re.compile(r"!\[\]\(r2:(.+)\)\Z")


def tidy_body(body: str, meta: dict) -> str:
    photos = meta.get("photos") or []
    names = [a["ta"] for a in meta.get("authors") or []]
    out: list[str] = []
    for block in body.split("\n\n"):
        text = block.strip()
        caption = CAPTION.fullmatch(text)
        if caption and out and out[-1].startswith("!["):
            picture = BARE_IMAGE.fullmatch(out[-1])
            if picture:
                key = picture.group(1)
                out[-1] = f"![{caption.group(1)}](r2:{key})"
                for photo in photos:
                    if photo["key"] == key and not photo["alt"]:
                        photo["alt"] = caption.group(1)
            continue
        bare = text.strip("*").strip()
        if len(out) < 4 and "\n" not in text and len(bare) < 70:
            if any(name and name in bare for name in names):
                continue
        out.append(block)
    return "\n\n".join(out)


def front_matter(meta: dict, body: str) -> str:
    import yaml

    head = yaml.dump(meta, allow_unicode=True, sort_keys=False, width=100).rstrip()
    out = f"---\n{head}\n---\n"
    return f"{out}\n{body}\n" if body else out


def build(src: Path) -> tuple[dict[str, tuple[dict, str]], list[dict], list[dict]]:
    """Returns {slug: (frontmatter, body)}, the people, and the photo manifest."""
    sections: dict[str, tuple[dict, str]] = {}
    photos: list[dict] = []

    people = write_people(src / PROFILES)
    quotes_meta: dict = {}

    for sec in SECTIONS:
        path = src / sec.source
        if not path.is_file():
            raise SystemExit(f"missing design file: {path}")
        if sec.type == "crossword":
            meta, body = write_crossword(sec, path)
        else:
            pages = section_pages(path, sec)
            if sec.type == "poem":
                meta, body = write_poem(sec, pages)
            elif sec.type in ("photos", "scans"):
                meta, body = write_photos(sec, pages)
            elif sec.type == "humour":
                meta, body = write_humour(sec, pages)
            elif sec.type == "spot-six":
                meta, body = write_spot_six(sec, pages)
            elif sec.type == "quotes":
                meta, body = write_quotes(sec, pages)
            elif sec.type == "profiles":
                meta, body = {"title": {"ta": sec.title}}, ""
            else:
                meta, body = write_prose(sec, pages)

        full = {
            "issue": "2026",
            "slug": sec.slug,
            "type": sec.type,
            **meta,
            "authors": [name_pair(a) for a in sec.authors],
            "source": f"{sec.source}" + (f" · pages {','.join(map(str, sec.pages))}" if sec.pages else ""),
        }
        kick = kicker_for(sec.type, full.get("kicker", ""))
        if kick:
            full["kicker"] = kick
        if body and sec.type in ("article", "memoir", "story"):
            body = tidy_body(body, full)
        if sec.type == "quotes":
            quotes_meta = full
        if not sec.page:
            continue
        sections[sec.slug] = (full, body)
        for p in full.get("photos", []) or []:
            photos.append(p)
        for key in ("answer_photo",):
            if full.get(key):
                photos.append(full[key])

    # Each person's closing quote comes off the சொல்ல மறந்த கதை spread.
    by_name = {q["by"]: q["text"] for q in quotes_meta.get("quotes", [])}
    for p in people:
        quote = by_name.get(p["name"]["ta"])
        if quote:
            p["quote"] = quote
        for key in ("photo_then", "photo_now"):
            if key in p:
                photos.append(p[key])

    return sections, people, photos


def cmd_apply(src: Path, apply: bool) -> int:
    sections, people, photos = build(src)
    order = [s.slug for s in SECTIONS if s.page]

    print(f"{len(sections)} reading pages, {len(people)} people, {len(photos)} photos\n")
    for sec in SECTIONS:
        if not sec.page:
            continue
        meta, body = sections[sec.slug]
        bits = [f"{meta['type']:9}", f"{meta['title']['ta'][:34]:36}"]
        if meta.get("authors"):
            bits.append("· ".join(f"{a['ta']} ({a['en']})" for a in meta["authors"]))
        print(f"  {sec.slug:26} {' '.join(bits)}  ({len(body)} chars)")
    print()
    missing = [p["name"]["ta"] for p in people if "photo_then" not in p]
    if missing:
        print(f"  no அன்று photo yet: {', '.join(missing)}")
    noquote = [p["name"]["ta"] for p in people if "quote" not in p]
    if noquote:
        print(f"  no closing quote:   {', '.join(noquote)}")
    print()

    if not apply:
        print("dry run — pass --apply to write the content files")
        return 0

    import yaml

    OUT_SECTIONS.mkdir(parents=True, exist_ok=True)
    OUT_PEOPLE.mkdir(parents=True, exist_ok=True)
    for slug, (meta, body) in sections.items():
        (OUT_SECTIONS / f"{slug}.md").write_text(front_matter(meta, body), encoding="utf-8")
    for stale in sorted(OUT_SECTIONS.glob("*.md")):
        if stale.stem not in sections:
            print(f"  removed {stale.name}, no longer a reading page")
            stale.unlink()
    for p in people:
        path = OUT_PEOPLE / f"{p['slug']}.yaml"
        path.write_text(
            yaml.dump(person_file(p, path), allow_unicode=True, sort_keys=False, width=100),
            encoding="utf-8",
        )

    issue = {
        "id": "2026",
        "kind": "annual",
        "year": 2026,
        "title": {"en": "Arivu Malar — 2026", "ta": "அறிவு மலர் — 2026"},
        "visibility": "public",
        "pages": 71,
        "cover": "public/arivumalar/2026/cover-front.webp",
        "cover_back": "public/arivumalar/2026/cover-back.webp",
        "pdf": "public/arivumalar/2026/arivumalar-2026.pdf",
        "pdf_bytes": 39545164,
        "editors": ["சரவணன்"],
        # The reading order. Change this list to reorder the web edition.
        "order": order,
    }
    (OUT_SECTIONS.parent.parent / "2026.yaml").write_text(
        yaml.dump(issue, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8"
    )

    out = Path(__file__).resolve().parent / "out"
    out.mkdir(exist_ok=True)
    seen: dict[str, dict] = {}
    for p in photos:
        seen.setdefault(p["key"], p)
    (out / "photos.json").write_text(
        json.dumps(sorted(seen.values(), key=lambda p: p["key"]), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(sections)} sections, {len(people)} people, {len(seen)} photo entries")
    return 0


def cmd_dump(src: Path, pattern: str) -> int:
    files = sorted(p for p in src.glob("*.dc.html") if pattern in p.name)
    if not files:
        print(f"no design file matches {pattern!r}", file=sys.stderr)
        return 1
    for path in files:
        print(f"######## {path.name}")
        for label, node in pages_of(parse(path)):
            print(f"==== page: {label}")
            for b in blocks_of(node):
                print("   ", json.dumps(b.as_dict(), ensure_ascii=False))
    return 0


def bare(text: str) -> str:
    """Only the letters: Markdown punctuation, whitespace and the numbers that the
    design draws as badges are stripped from both sides before comparing."""
    return re.sub(r"[\s>#*\\~—–\d-]+", "", text)


# Text the web edition leaves out on purpose, and why.
DROPPED = {
    "குமரவேல் நாராயணன் — தொடர்ச்சி": "the continuation page folds into one web page",
    "விளையாட்டு · விடைகள்": "the answers sit behind a விடைகள் button, not on their own page",
    "ஆறு வித்தியாசங்கள்": "the answers' own page heading, not needed once they are inline",
    "குறுக்கெழுத்துப் போட்டி — விடைகள்": "same, for the crossword",
    "சொல்ல மறந்த கதை": "now the heading above each person's own closing quote (ebook.untold_story)",
}


def cmd_verify(src: Path) -> int:
    """Check that every run of text in the design ended up in a content file."""
    sections, people, _ = build(src)
    written = {}
    for slug, (meta, body) in sections.items():
        import yaml

        written[slug] = bare(yaml.dump(meta, allow_unicode=True) + body)
    everything = "".join(written.values()) + bare(
        __import__("yaml").dump(people, allow_unicode=True)
    )

    misses = 0
    for sec in SECTIONS:
        if sec.type == "crossword":
            continue  # its text lives in the file's script, checked by the parse itself
        for blocks in section_pages(src / sec.source, sec):
            for b in blocks:
                if b.kind in ("furniture", "image") or not b.text:
                    continue
                if bare(b.text) in written.get(sec.slug, "") or bare(b.text) in everything:
                    continue
                if b.text in DROPPED:
                    continue
                misses += 1
                print(f"  MISSING from {sec.slug}: {b.kind} · {b.text[:70]}")
    print(f"\n{'no text lost' if not misses else str(misses) + ' blocks unaccounted for'}")
    return 1 if misses else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC, help="the design/ folder of the export")
    ap.add_argument("--dump", metavar="SUBSTRING", help="print classified blocks for matching design files")
    ap.add_argument("--apply", action="store_true", help="write the content files (otherwise dry run)")
    ap.add_argument("--verify", action="store_true", help="check that no text was dropped")
    args = ap.parse_args(argv)

    if not args.src.is_dir():
        print(f"not a directory: {args.src}", file=sys.stderr)
        return 1
    if args.dump:
        return cmd_dump(args.src, args.dump)
    if args.verify:
        return cmd_verify(args.src)
    return cmd_apply(args.src, args.apply)


if __name__ == "__main__":
    sys.exit(main())
