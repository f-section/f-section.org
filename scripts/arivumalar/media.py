"""Convert the Arivu Malar e-book pictures to WebP and stage them for R2.

Reads `out/photos.json` (written by extract.py) plus the two cover PNGs, writes a tree
under /mnt/data/f-section that mirrors the R2 keys exactly, and records each picture's
size in src/lib/ebook-img.json so the pages can reserve the right space before the
picture loads.

Nothing is uploaded here. Print the upload command with --upload-command, run it as a
dry run, and only then ask Saran (CLAUDE.md rule 3: `rclone copy`, never `sync`).

    scripts/ingest/.venv/bin/python scripts/arivumalar/media.py          # convert
    scripts/ingest/.venv/bin/python scripts/arivumalar/media.py --upload-command
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).resolve().parent / "out" / "photos.json"
SIZES = REPO / "src" / "lib" / "ebook-img.json"

WORK = Path("/mnt/data/f-section/arivumalar/2026")
EXPORT = WORK / "incoming" / "claude-design-arivumalar-source"
DESIGN = EXPORT / "design"
PDF_SRC = WORK / "incoming" / "Arivumalar-Full-book.pdf"
STAGE = WORK / "r2"  # STAGE/<r2 key> — so `rclone copy STAGE r2:bucket` lands right

PREFIX = "public/arivumalar/2026"
# One copy per picture, not a thumb/display pair: these sit in running text at about
# 34em, and the viewer only enlarges them to fit the screen. 1600px is enough for both
# and keeps the whole issue near 12 MB (rule 8).
MAX_EDGE = 1600
WEBP_QUALITY = 80

# The two covers live at the root of the export, under their Tamil names.
COVERS = {
    f"{PREFIX}/cover-front.webp": "முன்_அட்டை.png",
    f"{PREFIX}/cover-back.webp": "பின்_அட்டை.png",
}


def convert(src: Path, dest: Path) -> tuple[int, int]:
    """One WebP copy, upright, never upscaled. Returns its size in pixels."""
    from PIL import Image, ImageOps

    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        im.thumbnail((MAX_EDGE, MAX_EDGE))
        dest.parent.mkdir(parents=True, exist_ok=True)
        # No EXIF: these are scans and design assets, and the gallery's reasons for
        # keeping it (date, GPS) do not apply here.
        im.save(dest, "WEBP", quality=WEBP_QUALITY, method=6)
        return im.size


def human(n: int) -> str:
    return f"{n / 1024**2:.1f} MB" if n >= 1024**2 else f"{n / 1024:.0f} KB"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upload-command", action="store_true", help="print the rclone commands and stop")
    args = ap.parse_args(argv)

    if args.upload_command:
        print(f"# dry run first — nothing is written to R2:\n"
              f"rclone copy --immutable --dry-run -v {STAGE} r2:f-section-media\n\n"
              f"# then, only after Saran says yes:\n"
              f"rclone copy --immutable -v {STAGE} r2:f-section-media")
        return 0

    photos = json.loads(MANIFEST.read_text(encoding="utf-8"))
    jobs: list[tuple[str, Path]] = [(p["key"], DESIGN / p["source"]) for p in photos]
    jobs += [(key, EXPORT / name) for key, name in COVERS.items()]

    sizes: dict[str, list[int]] = {}
    missing = [src for _, src in jobs if not src.is_file()]
    if missing:
        for src in missing:
            print(f"missing source: {src}", file=sys.stderr)
        return 1

    for key, src in jobs:
        dest = STAGE / key
        w, h = convert(src, dest)
        sizes[key] = [w, h]

    pdf = STAGE / PREFIX / "arivumalar-2026.pdf"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    if not pdf.is_file() or pdf.stat().st_size != PDF_SRC.stat().st_size:
        shutil.copy2(PDF_SRC, pdf)

    SIZES.write_text(
        json.dumps(dict(sorted(sizes.items())), indent=0, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    pictures = sum((STAGE / k).stat().st_size for k in sizes)
    print(f"{len(sizes)} pictures  {human(pictures)}")
    print(f"the printable book  {human(pdf.stat().st_size)}")
    print(f"total               {human(pictures + pdf.stat().st_size)}")
    print(f"\nstaged in {STAGE}/{PREFIX}/")
    print(f"sizes written to {SIZES.relative_to(REPO)}")
    print("\nnext: --upload-command, run the dry run, then ask Saran before uploading")
    return 0


if __name__ == "__main__":
    sys.exit(main())
