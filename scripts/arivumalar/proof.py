"""Render the extracted Arivu Malar content as one HTML sheet for Saran to proofread.

    python3 -I scripts/arivumalar/proof.py [--out PATH]

This is a reading proof, not the website: it shows every section in reading order and
every profile, at the site's 18px Noto Sans Tamil on paper, so the Tamil can be checked
against the printed book. Photographs are not uploaded yet, so each one shows as a thin
marker line saying which file belongs there.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
ISSUE = REPO / "src" / "content" / "arivumalar" / "2026.yaml"
SECTIONS = REPO / "src" / "content" / "arivumalar" / "2026" / "sections"
PEOPLE = REPO / "src" / "content" / "arivumalar" / "2026" / "people"

CSS = """
:root { --paper:#F6F1E7; --card:#FFFDF7; --ink:#1E2A3A; --ink-red:#A23B2A; --sepia:#846541; }
* { box-sizing:border-box }
body { margin:0; background:var(--paper); color:var(--ink);
  font-family:'Noto Sans Tamil',system-ui,sans-serif; font-size:18px; line-height:1.8 }
main { max-width:40rem; margin:0 auto; padding:1.5rem 1rem 6rem }
h1 { font-size:1.7rem; line-height:1.3; margin:0 0 .25rem }
h2 { font-size:1.45rem; line-height:1.35; margin:0 0 .2rem; color:var(--ink-red) }
h3 { font-size:1.15rem; line-height:1.4; margin:2rem 0 .4rem; color:var(--ink-red) }
p { margin:0 0 1rem }
blockquote { margin:1.25rem 0; padding:.1rem 0 .1rem 1rem;
  border-left:3px solid var(--ink-red); color:var(--sepia) }
blockquote p:last-child { margin-bottom:0 }
.sheet { background:var(--card); border-radius:14px; padding:1.25rem 1.1rem;
  margin:0 0 1.5rem; box-shadow:0 1px 3px rgba(60,45,25,.12) }
.sheet.dark { background:#12100e; color:#efe2cb }
.sheet.dark h2, .sheet.dark h3 { color:#e8b563 }
.sheet.dark .meta { color:#bda781 }
.n { float:right; font-size:.8rem; color:var(--sepia); font-variant-numeric:tabular-nums }
.kicker { font-size:.78rem; letter-spacing:.14em; text-transform:uppercase; color:var(--sepia);
  margin:0 0 .35rem }
.meta { font-size:.82rem; color:var(--sepia); margin:.4rem 0 1rem;
  border-bottom:1px solid rgba(132,101,65,.25); padding-bottom:.6rem }
.poem p { margin:0 0 1.1rem }
.photo { font-size:.8rem; color:var(--sepia); background:rgba(132,101,65,.08);
  border:1px dashed rgba(132,101,65,.4); border-radius:8px; padding:.4rem .6rem; margin:1rem 0 }
.note { font-size:.9rem; color:var(--sepia) }
.fields { margin:0 0 1rem }
.fields dt { font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; color:var(--sepia);
  margin-top:.9rem }
.fields dd { margin:.1rem 0 0 }
.panel { background:rgba(132,101,65,.09); border-radius:10px; padding:.7rem .9rem; margin:.9rem 0 }
.panel .lbl { color:var(--ink-red); font-weight:600; display:block; margin-bottom:.2rem }
.grid { display:grid; gap:2px; margin:1rem 0; max-width:100% }
.cell { aspect-ratio:1; display:grid; place-items:center; font-size:.72rem;
  background:var(--card); border:1px solid rgba(30,42,58,.25); position:relative }
.cell.off { background:rgba(30,42,58,.82); border-color:transparent }
.cell b { position:absolute; top:1px; left:2px; font-size:.5rem; font-weight:600; color:var(--sepia) }
.clues { display:grid; grid-template-columns:1fr 1fr; gap:1rem; font-size:.9rem }
.clues ol { margin:.2rem 0; padding-left:1.4rem }
.joke { margin:0 0 1.4rem }
.joke .setup { font-size:.9rem; color:var(--sepia); margin-bottom:.4rem }
.joke .who { color:var(--ink-red); font-weight:600 }
.quote { margin:0 0 1.3rem }
.quote .by { display:block; text-align:right; color:var(--ink-red) }
hr { border:0; border-top:1px solid rgba(132,101,65,.3); margin:2.5rem 0 }
.top { font-size:.9rem; color:var(--sepia); margin:0 0 1.5rem }
"""


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def photo_marker(src: str, alt: str) -> str:
    bit = f" · alt: {esc(alt)}" if alt else " · no alt text, on purpose"
    return f'<p class="photo">படம் — <code>{esc(src)}</code>{bit}</p>'


def body_html(body: str, photos: list[dict], poem: bool) -> str:
    """The small Markdown subset that extract.py writes, turned into HTML."""
    by_key = {p["key"]: p for p in photos}
    out: list[str] = []
    for block in body.split("\n\n"):
        block = block.strip("\n")
        if not block:
            continue
        if m := re.fullmatch(r"!\[(.*?)\]\(r2:(.+?)\)", block, re.S):
            photo = by_key.get(m.group(2), {})
            out.append(photo_marker(photo.get("source", m.group(2)), m.group(1)))
        elif block.startswith("## "):
            out.append(f"<h3>{esc(block[3:])}</h3>")
        elif block.startswith(">"):
            paras = []
            for part in block.split("\n>\n"):
                lines = [ln.lstrip("> ").rstrip() for ln in part.split("\n")]
                paras.append("<p>" + "<br>".join(esc(ln) for ln in lines if ln) + "</p>")
            out.append("<blockquote>" + "".join(paras) + "</blockquote>")
        elif block.startswith("*") and block.endswith("*") and "\n" not in block:
            out.append(f'<p class="note"><em>{esc(block.strip("*"))}</em></p>')
        else:
            lines = block.split("\\\n")
            out.append("<p>" + "<br>".join(esc(ln) for ln in lines) + "</p>")
    return f'<div class="poem">{"".join(out)}</div>' if poem else "".join(out)


def crossword_html(m: dict) -> str:
    rows = [r.split("|") for r in m["grid"]]
    nums = [r.split("|") for r in m["numbers"]]
    cols = max(len(r) for r in rows)
    cells = []
    for r, row in enumerate(rows):
        for c in range(cols):
            ch = row[c] if c < len(row) else ""
            n = nums[r][c] if r < len(nums) and c < len(nums[r]) else ""
            if not ch:
                cells.append('<div class="cell off"></div>')
            else:
                cells.append(f'<div class="cell">{f"<b>{n}</b>" if n else ""}{esc(ch)}</div>')
    grid = f'<div class="grid" style="grid-template-columns:repeat({cols},1fr)">{"".join(cells)}</div>'
    def clue_list(key: str, label: str) -> str:
        items = "".join(
            f'<li value="{q["n"]}">{esc(q["clue"])} <strong>{esc(q["answer"])}</strong></li>'
            for q in m[key]
        )
        return f"<div><h3>{label}</h3><ol>{items}</ol></div>"
    return grid + '<div class="clues">' + clue_list("across", "இடமிருந்து வலம்") + clue_list(
        "down", "மேலிருந்து கீழ்"
    ) + "</div>"


def section_html(n: int, slug: str, m: dict, body: str) -> str:
    bits: list[str] = []
    bits.append(f'<span class="n">{n} / 29</span>')
    if m.get("kicker"):
        bits.append(f'<p class="kicker">{esc(m["kicker"])}</p>')
    if m.get("dedication"):
        bits.append(f'<p class="note">{"<br>".join(esc(x) for x in m["dedication"].split(chr(10)))}</p>')
    bits.append(f'<h2>{esc(m["title"]["ta"])}</h2>')
    who = ", ".join(a["ta"] for a in m.get("authors") or [])
    meta = [x for x in (who, m.get("byline", ""), m["type"], f"<code>{slug}</code>") if x]
    bits.append(f'<p class="meta">{" · ".join(meta)}<br>{esc(m.get("source", ""))}</p>')

    if m["type"] == "crossword":
        if m.get("note"):
            bits.append(f'<p class="note">{esc(m["note"])}</p>')
        bits.append(crossword_html(m))
    elif m["type"] == "humour":
        for joke in m.get("jokes", []):
            lines = "".join(
                f'<p><span class="who">{esc(l["speaker"])}</span> — {esc(l["text"])}</p>'
                for l in joke["lines"]
            )
            setup = f'<p class="setup">{esc(joke["setup"])}</p>' if joke.get("setup") else ""
            bits.append(f'<div class="joke">{setup}{lines}</div>')
    elif m["type"] == "quotes":
        for q in m.get("quotes", []):
            bits.append(
                f'<div class="quote"><p>{esc(q["text"])}</p>'
                f'<span class="by">— {esc(q["by"])}</span></div>'
            )
    elif m["type"] == "profiles":
        bits.append('<p class="note">The 19 profile pages follow at the end of this sheet.</p>')
    else:
        if m.get("note") and m["type"] == "spot-six":
            bits.append(f'<p class="note">{esc(m["note"])}</p>')
        for p in m.get("photos", []):
            bits.append(photo_marker(p["source"], p.get("alt", "")))
            if p.get("caption"):
                bits.append(f'<p class="note">{esc(p["caption"])}</p>')
        bits.append(body_html(body, m.get("photos", []), m["type"] == "poem"))
        if m.get("answers"):
            items = "".join(f'<li value="{a["n"]}">{esc(a["text"])}</li>' for a in m["answers"])
            bits.append(f'<h3>விடைகள்</h3><ol>{items}</ol>')
            if m.get("answer_photo"):
                bits.append(photo_marker(m["answer_photo"]["source"], m["answer_photo"].get("alt", "")))
        if m.get("note") and m["type"] == "poem":
            bits.append(f'<p class="note">{esc(m["note"])}</p>')
    cls = "sheet dark" if m.get("dark") else "sheet"
    return f'<section class="{cls}">{"".join(bits)}</section>'


def person_html(p: dict) -> str:
    bits = [f'<span class="n">{p["order"]}</span>', f'<h2>{esc(p["name"]["ta"])}</h2>']
    meta = [p["city"], f'printed as {esc(p["printed_name"])}', f'<code>{p["slug"]}</code>']
    bits.append(f'<p class="meta">{" · ".join(x for x in meta if x)}</p>')
    for key, when in (("photo_then", "அன்று"), ("photo_now", "இன்று")):
        if p.get(key):
            bits.append(photo_marker(f'{when} — {p[key]["source"]}', ""))
        else:
            bits.append(f'<p class="photo">{when} — <strong>missing, to crop from the printed book</strong></p>')
    if p.get("fields"):
        rows = "".join(
            f'<dt>{esc(f["label"])}</dt><dd>{"<br>".join(esc(x) for x in f["value"].split(chr(10)))}</dd>'
            for f in p["fields"]
        )
        bits.append(f'<dl class="fields">{rows}</dl>')
    for panel in p.get("panels", []):
        value = "<br>".join(esc(x) for x in panel["value"].split("\n"))
        bits.append(f'<div class="panel"><span class="lbl">{esc(panel["label"])}</span>{value}</div>')
    if p.get("quote"):
        bits.append('<p class="kicker">சொல்ல மறந்த கதை</p>')
        bits.append(f'<blockquote><p>{esc(p["quote"])}</p></blockquote>')
    else:
        bits.append('<p class="note">No closing quote in the book.</p>')
    return f'<section class="sheet">{"".join(bits)}</section>'


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("/mnt/data/f-section/review/arivumalar-proof.html"))
    args = ap.parse_args(argv)

    issue = yaml.safe_load(ISSUE.read_text(encoding="utf-8"))
    parts: list[str] = []
    for n, slug in enumerate(issue["order"], 1):
        text = (SECTIONS / f"{slug}.md").read_text(encoding="utf-8")
        head, _, body = text.partition("\n---\n")
        parts.append(section_html(n, slug, yaml.safe_load(head.lstrip("-\n")), body.strip()))

    people = sorted(
        (yaml.safe_load(p.read_text(encoding="utf-8")) for p in PEOPLE.glob("*.yaml")),
        key=lambda p: p["order"],
    )
    parts.append("<hr><h1>அன்றும் இன்றும்</h1>")
    parts.append(f'<p class="top">{len(people)} people, in the book\'s own order.</p>')
    parts.extend(person_html(p) for p in people)

    page = f"""<!doctype html>
<html lang="ta">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>அறிவு மலர் 2026 — proof</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
<main>
<h1>அறிவு மலர் 2026</h1>
<p class="top">Proof sheet, {len(issue["order"])} reading pages and {len(people)} profiles, in web
reading order. Text verbatim from the Claude Design export. Photographs are not uploaded yet, so
each shows as a marker line. 18px Noto Sans Tamil on paper, the site's own look.</p>
{"".join(parts)}
</main>
</html>
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    print(f"wrote {args.out} ({len(page):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
